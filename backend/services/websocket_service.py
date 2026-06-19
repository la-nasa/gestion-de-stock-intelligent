"""
Service d'envoi de messages WebSocket.
"""
import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from typing import Dict, Any, Optional


class WebSocketService:
    """Service pour envoyer des messages via WebSocket."""
    
    @staticmethod
    def get_channel():
        """Récupère la couche de canal."""
        return get_channel_layer()
    
    @staticmethod
    def send_to_user(user_id: str, event_type: str, data: Dict[str, Any]):
        """Envoie un message à un utilisateur spécifique."""
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        
        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': event_type,
                **data,
            }
        )
    
    @staticmethod
    def send_notification(user_id: str, notification: Dict[str, Any]):
        """Envoie une notification à un utilisateur."""
        WebSocketService.send_to_user(
            user_id,
            'notification_message',
            {'notification': notification}
        )
        
        # Mise à jour du compteur
        from apps.notifications.models import Notification
        count = Notification.objects.filter(
            recipient_id=user_id,
            is_read=False,
        ).count()
        
        WebSocketService.send_to_user(
            user_id,
            'unread_count_update',
            {'count': count}
        )
    
    @staticmethod
    def send_stock_update(product_id: str, data: Dict[str, Any]):
        """Envoie une mise à jour de stock."""
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        
        async_to_sync(channel_layer.group_send)(
            f'product_{product_id}',
            {
                'type': 'stock_update',
                'product_id': product_id,
                'data': data,
            }
        )
    
    @staticmethod
    def send_low_stock_alert(alert_data: Dict[str, Any]):
        """Envoie une alerte de stock bas à tous les managers."""
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        
        async_to_sync(channel_layer.group_send)(
            'stock_updates',
            {
                'type': 'low_stock_alert',
                'alert': alert_data,
            }
        )
        
        # Notifier aussi les utilisateurs spécifiques
        from apps.accounts.models import User
        managers = User.objects.filter(
            role__in=['ADMIN', 'MANAGER'],
            is_active=True,
        )
        for manager in managers:
            WebSocketService.send_notification(
                str(manager.id),
                {
                    'type': 'STOCK_LOW',
                    'title': '⚠️ Stock bas',
                    'message': f"Stock bas pour {alert_data.get('product_name', 'produit')}",
                    'priority': 1,
                }
            )
    
    @staticmethod
    def broadcast(message: str, level: str = 'info'):
        """Diffuse un message à tous les utilisateurs connectés."""
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        
        async_to_sync(channel_layer.group_send)(
            'broadcast',
            {
                'type': 'broadcast_message',
                'message': message,
                'level': level,
            }
        )
    
    @staticmethod
    def send_stock_movement(movement_data: Dict[str, Any]):
        """Envoie une notification de mouvement de stock."""
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        
        # Groupe global stock
        async_to_sync(channel_layer.group_send)(
            'stock_updates',
            {
                'type': 'stock_movement',
                'movement': movement_data,
            }
        )
        
        # Groupe warehouse spécifique
        warehouse_id = movement_data.get('warehouse_id')
        if warehouse_id:
            async_to_sync(channel_layer.group_send)(
                f'warehouse_{warehouse_id}',
                {
                    'type': 'stock_movement',
                    'movement': movement_data,
                }
            )