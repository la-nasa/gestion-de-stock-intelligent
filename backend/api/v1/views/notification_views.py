from rest_framework import views, status
from apps.notifications.models import Notification
from core.utils.response import success_response, error_response

class NotificationListView(views.APIView):
    def get(self, request):
        # D'abord filtrer, puis slicer
        all_notifs = Notification.objects.filter(recipient=request.user, is_deleted=False).order_by("-created_at")
        unread_count = all_notifs.filter(is_read=False).count()
        notifs = all_notifs[:50]  # Slice APRES le filtre
        data = [{"id": str(n.id), "type": n.type, "title": n.title, "message": n.message, "is_read": n.is_read, "created_at": n.created_at.isoformat()} for n in notifs]
        return success_response(data={"notifications": data, "unread_count": unread_count})

class NotificationReadView(views.APIView):
    def post(self, request, pk):
        try:
            n = Notification.objects.get(id=pk, recipient=request.user)
            n.mark_as_read()
            return success_response(message="Marquée comme lue")
        except Notification.DoesNotExist:
            return error_response(message="Introuvable", status_code=404)

class NotificationReadAllView(views.APIView):
    def post(self, request):
        from django.utils import timezone
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
        return success_response(message="Toutes lues")
