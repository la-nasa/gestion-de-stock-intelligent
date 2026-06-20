from rest_framework import views, status
from apps.warehouses.models import Warehouse
from apps.campuses.models import Campus
from core.utils.response import success_response, error_response

class WarehouseListView(views.APIView):
    def get(self, request):
        whs = Warehouse.objects.filter(is_deleted=False).select_related("campus")
        data = [{"id": str(w.id), "name": w.name, "code": w.code, "campus_name": w.campus.name if w.campus else "", "campus_id": str(w.campus_id) if w.campus_id else None, "type": w.type, "status": w.status, "capacity": float(w.capacity), "address": w.address or ""} for w in whs]
        return success_response(data={"results": data, "count": len(data)})

class WarehouseDetailView(views.APIView):
    def get(self, request, pk):
        try:
            w = Warehouse.objects.get(id=pk, is_deleted=False)
            return success_response(data={"id": str(w.id), "name": w.name, "code": w.code, "campus_name": w.campus.name if w.campus else "", "campus_id": str(w.campus_id) if w.campus_id else None, "type": w.type, "status": w.status, "capacity": float(w.capacity), "address": w.address or ""})
        except Warehouse.DoesNotExist:
            return error_response(message="Entrepôt introuvable", status_code=404)

class WarehouseCreateView(views.APIView):
    def post(self, request):
        try:
            campus_id = request.data.get("campus_id")
            campus = Campus.objects.get(id=campus_id) if campus_id else Campus.objects.first()
            w = Warehouse.objects.create(
                name=request.data.get("name", ""), code=request.data.get("code", ""),
                campus=campus, type=request.data.get("type", "SECONDARY"),
                capacity=request.data.get("capacity", 0), address=request.data.get("address", "")
            )
            return success_response(data={"id": str(w.id), "name": w.name, "code": w.code}, message="Entrepôt créé", status_code=201)
        except Exception as e:
            return error_response(message=str(e), status_code=400)
