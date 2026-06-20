"""Vues pour la gestion des stocks."""
from rest_framework import views, status
from apps.stock_movements.models import Stock, StockMovement
from apps.stock_entries.models import StockEntry, StockEntryLine
from apps.stock_outputs.models import StockOutput, StockOutputLine
from apps.transfers.models import Transfer, TransferLine
from apps.warehouses.models import Warehouse
from apps.products.models import Product
from apps.suppliers.models import Supplier
from api.v1.serializers.stock_serializers import StockSerializer, StockMovementSerializer, StockEntrySerializer, StockOutputSerializer, TransferSerializer
from api.v1.permissions import IsOperator, IsManager
from core.utils.response import success_response, error_response


class StockListView(views.APIView):
    permission_classes = [IsOperator]
    def get(self, request):
        qs = Stock.objects.filter(is_deleted=False).select_related("product", "warehouse")
        warehouse = request.query_params.get("warehouse")
        if warehouse: qs = qs.filter(warehouse_id=warehouse)
        product = request.query_params.get("product")
        if product: qs = qs.filter(product_id=product)
        data = [{"id": str(s.id), "product_name": s.product.name, "product_reference": s.product.reference, "warehouse_name": s.warehouse.name, "warehouse": str(s.warehouse_id), "quantity": s.quantity, "reserved_quantity": s.reserved_quantity, "available_quantity": s.available_quantity, "unit_price": float(s.unit_price), "location": s.location or "", "status": "out_of_stock" if s.quantity <= 0 else ("low" if s.quantity <= s.product.min_stock else "normal"), "last_movement_date": s.last_movement_date.isoformat() if s.last_movement_date else None} for s in qs]
        return success_response(data={"results": data, "count": len(data)})

class StockDetailView(views.APIView):
    permission_classes = [IsOperator]
    def get(self, request, pk):
        try:
            s = Stock.objects.get(id=pk, is_deleted=False)
            return success_response(data=StockSerializer(s).data)
        except Stock.DoesNotExist:
            return error_response(message="Stock introuvable", status_code=404)

class StockMovementListView(views.APIView):
    permission_classes = [IsOperator]
    def get(self, request):
        qs = StockMovement.objects.filter(is_deleted=False).select_related("stock__product", "stock__warehouse", "performed_by").order_by("-created_at")[:100]
        data = [{"id": str(m.id), "movement_type": m.movement_type, "reason": m.reason, "product_name": m.stock.product.name, "warehouse_name": m.stock.warehouse.name, "quantity": m.quantity, "unit_price": float(m.unit_price), "total_price": float(m.total_price), "performed_by_name": m.performed_by.get_full_name() if m.performed_by else "", "is_validated": m.is_validated, "created_at": m.created_at.isoformat()} for m in qs]
        return success_response(data={"results": data, "count": len(data)})

class StockEntryListView(views.APIView):
    permission_classes = [IsOperator]
    def get(self, request):
        qs = StockEntry.objects.filter(is_deleted=False).select_related("warehouse", "supplier").order_by("-entry_date")
        data = [{"id": str(e.id), "reference": e.reference, "supplier_name": e.supplier.name if e.supplier else "", "entry_date": e.entry_date.isoformat() if e.entry_date else None, "total_amount": float(e.total_amount), "status": e.status} for e in qs]
        return success_response(data={"results": data, "count": len(data)})

class StockEntryDetailView(views.APIView):
    permission_classes = [IsOperator]
    def get(self, request, pk):
        try:
            e = StockEntry.objects.get(id=pk, is_deleted=False)
            lines = [{"product_name": l.product.name, "quantity": l.quantity, "unit_price": float(l.unit_price), "total_price": float(l.total_price)} for l in e.lines.all()]
            return success_response(data={"id": str(e.id), "reference": e.reference, "supplier_name": e.supplier.name if e.supplier else "", "entry_date": e.entry_date.isoformat() if e.entry_date else None, "total_amount": float(e.total_amount), "status": e.status, "lines": lines})
        except StockEntry.DoesNotExist:
            return error_response(message="Entrée introuvable", status_code=404)

class StockEntryCreateView(views.APIView):
    permission_classes = [IsManager]
    def post(self, request):
        try:
            wh_id = request.data.get("warehouse_id")
            supplier_id = request.data.get("supplier_id")
            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity", 0))
            unit_price = float(request.data.get("unit_price", 0))
            
            if not wh_id: return error_response(message="Entrepôt requis", status_code=400)
            if not product_id: return error_response(message="Produit requis", status_code=400)
            if quantity <= 0: return error_response(message="Quantité invalide", status_code=400)
            
            wh = Warehouse.objects.get(id=wh_id)
            product = Product.objects.get(id=product_id)
            supplier = Supplier.objects.get(id=supplier_id) if supplier_id else None
            
            entry = StockEntry.objects.create(warehouse=wh, supplier=supplier, received_by=request.user, notes=request.data.get("notes", ""))
            StockEntryLine.objects.create(entry=entry, product=product, quantity=quantity, unit_price=unit_price)
            entry.total_amount = quantity * unit_price
            entry.save()
            
            return success_response(data={"id": str(entry.id), "reference": entry.reference}, message="Entrée créée", status_code=201)
        except Warehouse.DoesNotExist: return error_response(message="Entrepôt introuvable", status_code=400)
        except Product.DoesNotExist: return error_response(message="Produit introuvable", status_code=400)
        except Exception as e: return error_response(message=str(e), status_code=400)

class StockOutputListView(views.APIView):
    permission_classes = [IsOperator]
    def get(self, request):
        qs = StockOutput.objects.filter(is_deleted=False).select_related("warehouse").order_by("-output_date")
        data = [{"id": str(o.id), "reference": o.reference, "reason": o.reason, "output_date": o.output_date.isoformat() if o.output_date else None, "total_amount": float(o.total_amount), "status": o.status} for o in qs]
        return success_response(data={"results": data, "count": len(data)})

class StockOutputCreateView(views.APIView):
    permission_classes = [IsManager]
    def post(self, request):
        try:
            wh_id = request.data.get("warehouse_id")
            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity", 0))
            
            if not wh_id: return error_response(message="Entrepôt requis", status_code=400)
            if not product_id: return error_response(message="Produit requis", status_code=400)
            if quantity <= 0: return error_response(message="Quantité invalide", status_code=400)
            
            wh = Warehouse.objects.get(id=wh_id)
            product = Product.objects.get(id=product_id)
            
            output = StockOutput.objects.create(warehouse=wh, reason=request.data.get("reason", "INTERNAL_USE"), issued_by=request.user, notes=request.data.get("notes", ""))
            StockOutputLine.objects.create(output=output, product=product, quantity=quantity, unit_price=product.unit_price)
            output.total_amount = quantity * float(product.unit_price)
            output.save()
            
            return success_response(data={"id": str(output.id), "reference": output.reference}, message="Sortie créée", status_code=201)
        except Warehouse.DoesNotExist: return error_response(message="Entrepôt introuvable", status_code=400)
        except Product.DoesNotExist: return error_response(message="Produit introuvable", status_code=400)
        except Exception as e: return error_response(message=str(e), status_code=400)

class TransferListView(views.APIView):
    permission_classes = [IsOperator]
    def get(self, request):
        qs = Transfer.objects.filter(is_deleted=False).select_related("source_warehouse", "destination_warehouse")
        data = [{"id": str(t.id), "reference": t.reference, "source_name": t.source_warehouse.name, "destination_name": t.destination_warehouse.name, "total_items": t.total_items, "status": t.status} for t in qs]
        return success_response(data={"results": data, "count": len(data)})

class TransferCreateView(views.APIView):
    permission_classes = [IsManager]
    def post(self, request):
        try:
            src_id = request.data.get("source_warehouse_id")
            dst_id = request.data.get("destination_warehouse_id")
            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity", 0))
            
            if not src_id or not dst_id: return error_response(message="Entrepôts source et destination requis", status_code=400)
            if not product_id: return error_response(message="Produit requis", status_code=400)
            if quantity <= 0: return error_response(message="Quantité invalide", status_code=400)
            
            src = Warehouse.objects.get(id=src_id)
            dst = Warehouse.objects.get(id=dst_id)
            product = Product.objects.get(id=product_id)
            
            transfer = Transfer.objects.create(source_warehouse=src, destination_warehouse=dst, requested_by=request.user, notes=request.data.get("notes", ""))
            TransferLine.objects.create(transfer=transfer, product=product, quantity=quantity, unit_price=product.unit_price)
            transfer.total_items = quantity
            transfer.save()
            
            return success_response(data={"id": str(transfer.id), "reference": transfer.reference}, message="Transfert créé", status_code=201)
        except Warehouse.DoesNotExist: return error_response(message="Entrepôt introuvable", status_code=400)
        except Product.DoesNotExist: return error_response(message="Produit introuvable", status_code=400)
        except Exception as e: return error_response(message=str(e), status_code=400)
