"""Vues pour l'OCR de factures."""
from rest_framework import views, status, parsers
from services.ocr_service import OCRService
from apps.suppliers.models import Supplier
from apps.products.models import Product
from apps.stock_entries.models import StockEntry, StockEntryLine
from apps.purchase_orders.models import PurchaseOrder, PurchaseOrderLine
from api.v1.permissions import IsOperator, IsManager
from core.utils.response import success_response, error_response


class OCRInvoiceView(views.APIView):
    """Upload et OCR d'une facture."""
    
    permission_classes = [IsOperator]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    
    def post(self, request):
        """Upload une image de facture et extrait les données."""
        image_file = request.FILES.get('image')
        
        if not image_file:
            return error_response(
                message="Veuillez fournir une image de facture",
                status_code=400
            )
        
        # Vérifier le type de fichier
        allowed_types = ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp', 'application/pdf']
        if image_file.content_type not in allowed_types:
            return error_response(
                message=f"Format non supporté. Formats acceptés: JPEG, PNG, TIFF, BMP, PDF",
                status_code=400
            )
        
        # Vérifier la taille (max 10MB)
        if image_file.size > 10 * 1024 * 1024:
            return error_response(
                message="L'image ne doit pas dépasser 10 Mo",
                status_code=400
            )
        
        try:
            # Lire les données
            image_data = image_file.read()
            
            # Extraire les données
            extracted_data = OCRService.extract_invoice_data(image_data)
            
            # Essayer de faire correspondre avec les données existantes
            enriched_data = OCRInvoiceView._enrich_data(extracted_data)
            
            return success_response(
                data=enriched_data,
                message="Facture analysée avec succès"
            )
            
        except Exception as e:
            return error_response(
                message=f"Erreur lors de l'analyse: {str(e)}",
                status_code=500
            )
    
    @staticmethod
    def _enrich_data(data: dict) -> dict:
        """Enrichit les données extraites avec les correspondances en base."""
        enriched = dict(data)
        enriched['matches'] = {}
        
        # Chercher le fournisseur
        supplier_name = data.get('supplier_name')
        if supplier_name:
            from django.db.models import Q
            suppliers = Supplier.objects.filter(
                Q(name__icontains=supplier_name) | Q(tax_id__icontains=supplier_name)
            )[:5]
            enriched['matches']['suppliers'] = [{
                'id': str(s.id),
                'name': s.name,
                'code': s.code,
                'tax_id': s.tax_id,
            } for s in suppliers]
        
        # Chercher les produits correspondants
        items = data.get('items', [])
        if items:
            matched_items = []
            for item in items:
                desc = item.get('description', '')
                if desc:
                    products = Product.objects.filter(
                        Q(name__icontains=desc) | Q(reference__icontains=desc)
                    )[:3]
                    item['matches'] = [{
                        'id': str(p.id),
                        'name': p.name,
                        'reference': p.reference,
                        'unit_price': float(p.unit_price),
                    } for p in products]
                matched_items.append(item)
            enriched['items'] = matched_items
        
        return enriched


class OCRCreateEntryView(views.APIView):
    """Crée une entrée de stock à partir des données OCR."""
    
    permission_classes = [IsManager]
    
    def post(self, request):
        """Crée une entrée de stock avec les données validées."""
        supplier_id = request.data.get('supplier_id')
        items = request.data.get('items', [])
        invoice_number = request.data.get('invoice_number', '')
        invoice_date = request.data.get('date')
        warehouse_id = request.data.get('warehouse_id')
        
        if not supplier_id:
            return error_response(message="Fournisseur requis", status_code=400)
        if not items:
            return error_response(message="Aucun article à traiter", status_code=400)
        if not warehouse_id:
            return error_response(message="Entrepôt requis", status_code=400)
        
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            return error_response(message="Fournisseur introuvable", status_code=404)
        
        # Créer l'entrée de stock
        entry = StockEntry.objects.create(
            warehouse_id=warehouse_id,
            supplier=supplier,
            invoice_number=invoice_number,
            received_by=request.user,
            notes=f'Créé automatiquement par OCR. Facture: {invoice_number}',
        )
        
        # Créer les lignes
        created_items = []
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            
            if product_id and quantity > 0:
                try:
                    product = Product.objects.get(id=product_id)
                    line = StockEntryLine.objects.create(
                        entry=entry,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                    )
                    created_items.append({
                        'product': product.name,
                        'quantity': quantity,
                        'unit_price': float(unit_price),
                        'total': float(line.total_price),
                    })
                except Product.DoesNotExist:
                    pass
        
        # Mettre à jour le montant total
        entry.total_amount = sum(line.total_price for line in entry.lines.all())
        entry.save()
        
        return success_response(
            data={
                'entry_id': str(entry.id),
                'reference': entry.reference,
                'supplier': supplier.name,
                'items_count': len(created_items),
                'total_amount': float(entry.total_amount),
                'items': created_items,
            },
            message=f"Entrée de stock créée avec {len(created_items)} article(s)",
            status_code=201
        )