from rest_framework import views
from apps.campuses.models import Campus
from core.utils.response import success_response

class CampusListView(views.APIView):
    def get(self, request):
        campuses = Campus.objects.filter(is_deleted=False)
        data = [{"id": str(c.id), "name": c.name, "code": c.code, "city": c.city} for c in campuses]
        return success_response(data={"results": data, "count": len(data)})
