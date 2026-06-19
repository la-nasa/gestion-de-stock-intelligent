"""
Service de gestion des notifications.
"""
import json
from typing import List, Optional
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.notifications.models import Notification
from apps.accounts.models import User


class NotificationService:
    """Service d'envoi de notifications."""
    
    @staticmethod
    def send_notification(
        recipient: User,
        notification_type: str,
        title: str,
        message: str,
        link: str = '',
        channel: str = 'IN_APP',
        priority: int = 0,
        related_object_type: str = '',
        related_object_id: str = '',
    ) -> Notification:
        """Envoie une notification à un utilisateur."""
        
        notification = Notification.objects.create(
            recipient=recipient,
            type=notification_type,
            channel=channel,
            title=title,
            message=message,
            link=link,
            priority=priority,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
        )
        
        # Envoyer via WebSocket si IN_APP
        if channel == 'IN_APP':
            NotificationService._send_websocket(recipient, notification)
        
        # Envoyer par email si configuré
        if channel == 'EMAIL':
            NotificationService._send_email(recipient, notification)
        
        return notification
    
    @staticmethod
    def send_bulk_notifications(
        recipients: List[User],
        notification_type: str,
        title: str,
        message: str,
        **kwargs
    ) -> List[Notification]:
        """Envoie des notifications à plusieurs utilisateurs."""
        notifications = []
        for recipient in recipients:
            notification = NotificationService.send_notification(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                **kwargs
            )
            notifications.append(notification)
        return notifications
    
    @staticmethod
    def send_stock_alert(product, stock, alert_type: str):
        """Envoie une alerte de stock."""
        
        if alert_type == 'low_stock':
            title = '⚠️ Stock bas'
            message = f"Le stock de {product.name} ({product.reference}) est bas : {stock.quantity} unité(s) restante(s). Minimum : {product.min_stock}."
            notification_type = 'STOCK_LOW'
        elif alert_type == 'out_of_stock':
            title = '🚨 Rupture de stock'
            message = f"Rupture de stock pour {product.name} ({product.reference}) !"
            notification_type = 'STOCK_OUT'
        elif alert_type == 'reorder':
            title = '📦 Point de commande atteint'
            message = f"{product.name} a atteint son point de commande. Quantité optimale suggérée : {product.optimal_quantity}."
            notification_type = 'STOCK_LOW'
        else:
            return
        
        # Notifier les managers et superviseurs
        recipients = User.objects.filter(
            role__in=['ADMIN', 'MANAGER', 'SUPERVISOR'],
            is_active=True,
        )
        
        NotificationService.send_bulk_notifications(
            recipients=recipients,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_type='products.Product',
            related_object_id=str(product.id),
        )
        
        # Notifier via WebSocket
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'stock_updates',
                {
                    'type': 'low_stock_alert',
                    'alert': {
                        'product_id': str(product.id),
                        'product_name': product.name,
                        'reference': product.reference,
                        'current_stock': stock.quantity,
                        'min_stock': product.min_stock,
                        'alert_type': alert_type,
                    }
                }
            )
    
    @staticmethod
    def notify_inventory_completed(inventory):
        """Notification de fin d'inventaire."""
        title = '✅ Inventaire terminé'
        message = f"L'inventaire {inventory.reference} est terminé. {inventory.counted_items} articles comptés, {inventory.differences} écarts."
        
        recipients = User.objects.filter(
            role__in=['ADMIN', 'MANAGER'],
            is_active=True,
        )
        
        NotificationService.send_bulk_notifications(
            recipients=recipients,
            notification_type='SUCCESS',
            title=title,
            message=message,
            related_object_type='inventories.Inventory',
            related_object_id=str(inventory.id),
        )
    
    @staticmethod
    def notify_order_received(purchase_order):
        """Notification de réception de commande."""
        title = '📦 Commande reçue'
        message = f"La commande {purchase_order.reference} de {purchase_order.supplier.name} a été reçue."
        
        recipients = User.objects.filter(
            role__in=['ADMIN', 'MANAGER'],
            is_active=True,
        )
        
        NotificationService.send_bulk_notifications(
            recipients=recipients,
            notification_type='ORDER_RECEIVED',
            title=title,
            message=message,
            related_object_type='purchase_orders.PurchaseOrder',
            related_object_id=str(purchase_order.id),
        )
    
    @staticmethod
    def _send_websocket(user: User, notification: Notification):
        """Envoie une notification via WebSocket."""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user.id}',
                {
                    'type': 'notification_message',
                    'notification': {
                        'id': str(notification.id),
                        'type': notification.type,
                        'title': notification.title,
                        'message': notification.message,
                        'link': notification.link,
                        'priority': notification.priority,
                        'created_at': notification.created_at.isoformat(),
                    }
                }
            )
            
            # Mise à jour du compteur
            unread_count = Notification.objects.filter(
                recipient=user,
                is_read=False,
            ).count()
            
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user.id}',
                {
                    'type': 'unread_count',
                    'count': unread_count,
                }
            )
    
    @staticmethod
    def _send_email(user: User, notification: Notification):
        """Envoie une notification par email."""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            send_mail(
                subject=f'[IUC Inventory] {notification.title}',
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass