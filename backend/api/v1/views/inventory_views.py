"""Vues pour la gestion des inventaires."""
from rest_framework import views, status
from django.utils import timezone
from apps.inventories.models import Inventory, InventoryLine
from apps.stock_movements.models import Stock
from apps.warehouses.models import Warehouse
from api.v1.permissions import IsOperator, IsManager
from core.utils.response import success_response, error_response


class InventoryListView(views.APIView):
    permission_classes = [IsOperator]
    
    def get(self, request):
        inventories = Inventory.objects.filter(is_deleted=False).select_related("warehouse", "supervisor").order_by("-start_date")
        status_filter = request.query_params.get("status")
        if status_filter:
            inventories = inventories.filter(status=status_filter)
        warehouse = request.query_params.get("warehouse")
        if warehouse:
            inventories = inventories.filter(warehouse_id=warehouse)
        
        data = []
        for inv in inventories:
            data.append({
                "id": str(inv.id),
                "reference": inv.reference,
                "type": inv.type,
                "status": inv.status,
                "warehouse_id": str(inv.warehouse_id),
                "warehouse_name": inv.warehouse.name,
                "start_date": inv.start_date.isoformat() if inv.start_date else None,
                "end_date": inv.end_date.isoformat() if inv.end_date else None,
                "expected_items": inv.expected_items,
                "counted_items": inv.counted_items,
                "differences": inv.differences,
                "total_value_expected": float(inv.total_value_expected),
                "total_value_counted": float(inv.total_value_counted),
                "value_difference": float(inv.value_difference),
                "supervisor_name": inv.supervisor.get_full_name() if inv.supervisor else None,
            })
        return success_response(data={"results": data, "count": len(data)})
    
    def post(self, request):
        warehouse_id = request.data.get("warehouse_id")
        type_inv = request.data.get("type", "FULL")
        description = request.data.get("description", "")
        
        if not warehouse_id:
            return error_response(message="L'entrepôt est obligatoire", status_code=400)
        
        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
        except Warehouse.DoesNotExist:
            return error_response(message="Entrepôt introuvable", status_code=400)
        
        inventory = Inventory.objects.create(
            warehouse=warehouse,
            type=type_inv,
            status="PLANNED",
            start_date=timezone.now(),
            description=description,
            supervisor=request.user,
        )
        
        stocks = Stock.objects.filter(warehouse=warehouse, is_deleted=False).select_related("product")
        lines = []
        for stock in stocks:
            lines.append(InventoryLine(
                inventory=inventory,
                product=stock.product,
                expected_quantity=stock.quantity,
                unit_price=stock.unit_price,
            ))
        InventoryLine.objects.bulk_create(lines)
        
        inventory.expected_items = len(lines)
        inventory.total_value_expected = sum(line.expected_quantity * line.unit_price for line in lines)
        inventory.save()
        
        return success_response(
            data={"id": str(inventory.id), "reference": inventory.reference},
            message="Inventaire créé avec succès",
            status_code=201
        )


class InventoryDetailView(views.APIView):
    permission_classes = [IsOperator]
    
    def get(self, request, pk):
        try:
            inventory = Inventory.objects.get(id=pk, is_deleted=False)
        except Inventory.DoesNotExist:
            return error_response(message="Inventaire introuvable", status_code=404)
        
        lines = inventory.lines.select_related("product", "counted_by").all()
        data = {
            "id": str(inventory.id),
            "reference": inventory.reference,
            "type": inventory.type,
            "status": inventory.status,
            "warehouse_name": inventory.warehouse.name,
            "start_date": inventory.start_date.isoformat() if inventory.start_date else None,
            "supervisor_name": inventory.supervisor.get_full_name() if inventory.supervisor else None,
            "expected_items": inventory.expected_items,
            "counted_items": inventory.counted_items,
            "differences": inventory.differences,
            "total_value_expected": float(inventory.total_value_expected),
            "total_value_counted": float(inventory.total_value_counted),
            "value_difference": float(inventory.value_difference),
            "lines": [{
                "id": str(line.id),
                "product": str(line.product_id),
                "product_name": line.product.name,
                "product_reference": line.product.reference,
                "expected_quantity": line.expected_quantity,
                "counted_quantity": line.counted_quantity,
                "difference": line.difference,
                "unit_price": float(line.unit_price),
                "difference_value": float(line.difference_value),
                "counted_by_name": line.counted_by.get_full_name() if line.counted_by else None,
                "counted_at": line.counted_at.isoformat() if line.counted_at else None,
                "notes": line.notes,
            } for line in lines],
        }
        return success_response(data=data)


class InventoryLineUpdateView(views.APIView):
    permission_classes = [IsOperator]
    
    def patch(self, request, inventory_id, line_id):
        try:
            inventory = Inventory.objects.get(id=inventory_id, is_deleted=False, status="IN_PROGRESS")
        except Inventory.DoesNotExist:
            return error_response(message="Inventaire introuvable ou non modifiable", status_code=404)
        try:
            line = InventoryLine.objects.get(id=line_id, inventory=inventory)
        except InventoryLine.DoesNotExist:
            return error_response(message="Ligne introuvable", status_code=404)
        
        counted_quantity = request.data.get("counted_quantity")
        if counted_quantity is None:
            return error_response(message="Quantité comptée obligatoire", status_code=400)
        
        line.counted_quantity = int(counted_quantity)
        line.counted_by = request.user
        line.counted_at = timezone.now()
        line.save()
        
        lines = inventory.lines.all()
        inventory.counted_items = lines.filter(counted_quantity__isnull=False).count()
        inventory.differences = sum((l.counted_quantity or 0) - l.expected_quantity for l in lines if l.counted_quantity is not None)
        inventory.total_value_counted = sum((l.counted_quantity or 0) * l.unit_price for l in lines if l.counted_quantity is not None)
        inventory.value_difference = float(inventory.total_value_counted) - float(inventory.total_value_expected)
        inventory.save()
        
        return success_response(message="Comptage enregistré")


class InventoryValidateView(views.APIView):
    permission_classes = [IsManager]
    
    def post(self, request, pk):
        try:
            inventory = Inventory.objects.get(id=pk, is_deleted=False, status="IN_PROGRESS")
        except Inventory.DoesNotExist:
            return error_response(message="Inventaire introuvable ou non validable", status_code=404)
        
        inventory.status = "VALIDATED"
        inventory.end_date = timezone.now()
        inventory.save()
        
        for line in inventory.lines.filter(counted_quantity__isnull=False):
            try:
                stock = Stock.objects.get(product=line.product, warehouse=inventory.warehouse, is_deleted=False)
                stock.quantity = line.counted_quantity
                stock.last_inventory_date = timezone.now()
                stock.save()
            except Stock.DoesNotExist:
                pass
        
        return success_response(message="Inventaire validé avec succès")
