"""Vues pour les QR Codes et Barcodes."""
from rest_framework import views, status
from django.http import HttpResponse
from services.qr_service import QRCodeService
from apps.qr_codes.models import QRCode, Barcode, QRScanLog
from apps.products.models import Product
from api.v1.permissions import IsOperator, IsManager
from core.utils.response import success_response, error_response


class QRGenerateView(views.APIView):
    """Génération de QR code pour un produit."""
    
    permission_classes = [IsManager]
    
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
        except Product.DoesNotExist:
            return error_response(message="Produit introuvable", status_code=404)
        
        try:
            qr_code = QRCodeService.generate_qr_code(product)
            
            return success_response(
                data={
                    'id': str(qr_code.id),
                    'code': qr_code.code,
                    'image_url': qr_code.image.url if qr_code.image else None,
                    'product': str(product.id),
                },
                message="QR code généré avec succès",
                status_code=201
            )
        except Exception as e:
            return error_response(message=str(e), status_code=500)


class BarcodeGenerateView(views.APIView):
    """Génération de code-barres pour un produit."""
    
    permission_classes = [IsManager]
    
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
        except Product.DoesNotExist:
            return error_response(message="Produit introuvable", status_code=404)
        
        format_type = request.data.get('format', 'CODE128')
        
        try:
            barcode_obj = QRCodeService.generate_barcode(product, format_type)
            
            return success_response(
                data={
                    'id': str(barcode_obj.id),
                    'code': barcode_obj.code,
                    'format': barcode_obj.format,
                    'image_url': barcode_obj.image.url if barcode_obj.image else None,
                },
                message="Code-barres généré avec succès",
                status_code=201
            )
        except Exception as e:
            return error_response(message=str(e), status_code=500)


class QRScanView(views.APIView):
    """Scan d'un QR code."""
    
    permission_classes = [IsOperator]
    
    def post(self, request):
        qr_content = request.data.get('code')
        if not qr_content:
            return error_response(message="Code QR requis", status_code=400)
        
        product = QRCodeService.get_product_by_qr(qr_content)
        if not product:
            return error_response(message="Produit non trouvé pour ce QR code", status_code=404)
        
        # Logger le scan
        try:
            qr_code = QRCode.objects.get(code=qr_content)
            qr_code.increment_scan()
            
            QRScanLog.objects.create(
                qr_code=qr_code,
                scanned_by=request.user,
                ip_address=request.META.get('REMOTE_ADDR'),
                device_info=request.META.get('HTTP_USER_AGENT', ''),
                action='scan',
            )
        except QRCode.DoesNotExist:
            pass
        
        # Informations du produit
        stocks = product.stocks.filter(is_deleted=False).select_related('warehouse')
        
        return success_response(data={
            'product': {
                'id': str(product.id),
                'name': product.name,
                'reference': product.reference,
                'sku': product.sku,
                'unit_price': float(product.unit_price),
                'status': product.status,
            },
            'stocks': [{
                'warehouse': stock.warehouse.name,
                'quantity': stock.quantity,
                'available': stock.available_quantity,
                'location': stock.location,
            } for stock in stocks],
        })


class QRBulkPrintView(views.APIView):
    """Génération d'une planche de QR codes pour impression."""
    
    permission_classes = [IsManager]
    
    def post(self, request):
        product_ids = request.data.get('product_ids', [])
        if not product_ids:
            return error_response(message="Liste de produits requise", status_code=400)
        
        try:
            image_data = QRCodeService.generate_bulk_qr_codes(product_ids)
            
            response = HttpResponse(image_data, content_type='image/png')
            response['Content-Disposition'] = 'attachment; filename="qr_codes_planche.png"'
            return response
        except Exception as e:
            return error_response(message=str(e), status_code=500)


class ProductQRCodesView(views.APIView):
    """QR codes et barcodes d'un produit."""
    
    permission_classes = [IsOperator]
    
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
        except Product.DoesNotExist:
            return error_response(message="Produit introuvable", status_code=404)
        
        qr_code = QRCode.objects.filter(product=product, is_active=True).first()
        barcodes = Barcode.objects.filter(product=product, is_deleted=False)
        
        return success_response(data={
            'product': {
                'id': str(product.id),
                'name': product.name,
                'reference': product.reference,
            },
            'qr_code': {
                'id': str(qr_code.id) if qr_code else None,
                'code': qr_code.code if qr_code else None,
                'image_url': qr_code.image.url if qr_code and qr_code.image else None,
                'scan_count': qr_code.scan_count if qr_code else 0,
            } if qr_code else None,
            'barcodes': [{
                'id': str(b.id),
                'code': b.code,
                'format': b.format,
                'image_url': b.image.url if b.image else None,
                'is_primary': b.is_primary,
            } for b in barcodes],
        })