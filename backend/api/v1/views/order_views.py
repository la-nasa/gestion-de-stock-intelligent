from rest_framework import views, status
from apps.purchase_orders.models import PurchaseOrder
from apps.suppliers.models import Supplier
from core.utils.response import success_response, error_response

class PurchaseOrderListView(views.APIView):
    def get(self, request):
        orders = PurchaseOrder.objects.filter(is_deleted=False).select_related("supplier")
        data = [{"id": str(o.id), "reference": o.reference, "supplier_name": o.supplier.name if o.supplier else "", "supplier_id": str(o.supplier_id) if o.supplier_id else None, "order_date": str(o.order_date), "expected_delivery_date": str(o.expected_delivery_date) if o.expected_delivery_date else None, "total_amount": float(o.total_amount), "status": o.status, "notes": o.notes} for o in orders]
        return success_response(data={"results": data, "count": len(data)})

class PurchaseOrderDetailView(views.APIView):
    def get(self, request, pk):
        try:
            o = PurchaseOrder.objects.get(id=pk, is_deleted=False)
            lines = [{"id": str(l.id), "product_name": l.product.name, "quantity": l.quantity, "unit_price": float(l.unit_price), "total_price": float(l.total_price), "received_quantity": l.received_quantity} for l in o.lines.all()]
            return success_response(data={"id": str(o.id), "reference": o.reference, "supplier_name": o.supplier.name if o.supplier else "", "order_date": str(o.order_date), "total_amount": float(o.total_amount), "status": o.status, "notes": o.notes, "lines": lines})
        except PurchaseOrder.DoesNotExist:
            return error_response(message="Commande introuvable", status_code=404)

class PurchaseOrderCreateView(views.APIView):
    def post(self, request):
        try:
            supplier_id = request.data.get("supplier_id")
            supplier = Supplier.objects.get(id=supplier_id)
            o = PurchaseOrder.objects.create(supplier=supplier, status="DRAFT", notes=request.data.get("notes", ""))
            return success_response(data={"id": str(o.id), "reference": o.reference}, message="Commande créée", status_code=201)
        except Supplier.DoesNotExist:
            return error_response(message="Fournisseur introuvable", status_code=400)
        except Exception as e:
            return error_response(message=str(e), status_code=400)
