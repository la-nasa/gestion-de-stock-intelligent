"""Vues pour les notifications."""
from rest_framework import views, status
from apps.notifications.models import Notification
from api.v1.permissions import IsOperator
from core.utils.response import success_response, error_response


class NotificationListView(views.APIView):
    """Liste des notifications de l'utilisateur."""
    
    permission_classes = [IsOperator]
    
    def get(self, request):
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_deleted=False,
        ).order_by('-created_at')[:50]
        
        unread_count = notifications.filter(is_read=False).count()
        
        data = {
            'unread_count': unread_count,
            'notifications': [{
                'id': str(n.id),
                'type': n.type,
                'channel': n.channel,
                'title': n.title,
                'message': n.message,
                'link': n.link,
                'priority': n.priority,
                'is_read': n.is_read,
                'read_at': n.read_at.isoformat() if n.read_at else None,
                'created_at': n.created_at.isoformat(),
                'related_object_type': n.related_object_type,
                'related_object_id': n.related_object_id,
            } for n in notifications],
        }
        
        return success_response(data=data)


class NotificationReadView(views.APIView):
    """Marquer une notification comme lue."""
    
    permission_classes = [IsOperator]
    
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(
                id=pk,
                recipient=request.user,
            )
        except Notification.DoesNotExist:
            return error_response(message="Notification introuvable", status_code=404)
        
        notification.mark_as_read()
        return success_response(message="Notification marquée comme lue")


class NotificationReadAllView(views.APIView):
    """Marquer toutes les notifications comme lues."""
    
    permission_classes = [IsOperator]
    
    def post(self, request):
        from django.utils import timezone
        
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())
        
        return success_response(
            message=f"{updated} notification(s) marquée(s) comme lue(s)"
        )