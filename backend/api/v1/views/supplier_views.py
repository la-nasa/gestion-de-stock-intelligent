from rest_framework import views, status
from apps.suppliers.models import Supplier
from core.utils.response import success_response, error_response

class SupplierListView(views.APIView):
    def get(self, request):
        suppliers = Supplier.objects.filter(is_deleted=False)
        data = [{"id": str(s.id), "name": s.name, "code": s.code, "email": s.email, "phone": s.phone, "contact_person": s.contact_person, "city": s.city, "country": s.country, "category": s.category, "rating": s.rating, "status": s.status} for s in suppliers]
        return success_response(data={"results": data, "count": len(data)})

class SupplierDetailView(views.APIView):
    def get(self, request, pk):
        try:
            s = Supplier.objects.get(id=pk, is_deleted=False)
            return success_response(data={"id": str(s.id), "name": s.name, "code": s.code, "email": s.email, "phone": s.phone, "contact_person": s.contact_person, "city": s.city, "country": s.country, "category": s.category, "rating": s.rating, "status": s.status, "address": s.address, "website": s.website, "tax_id": s.tax_id})
        except Supplier.DoesNotExist:
            return error_response(message="Fournisseur introuvable", status_code=404)

class SupplierCreateView(views.APIView):
    def post(self, request):
        try:
            s = Supplier.objects.create(
                name=request.data.get("name", ""),
                code=request.data.get("code", ""),
                email=request.data.get("email", ""),
                phone=request.data.get("phone", ""),
                contact_person=request.data.get("contact_person", ""),
                city=request.data.get("city", ""),
                country=request.data.get("country", "Cameroun"),
                category=request.data.get("category", ""),
            )
            return success_response(data={"id": str(s.id), "name": s.name}, message="Fournisseur créé", status_code=201)
        except Exception as e:
            return error_response(message=str(e), status_code=400)
