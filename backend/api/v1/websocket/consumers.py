"""
Consommateurs WebSocket complets.
"""
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from apps.notifications.models import Notification
from apps.stock_movements.models import Stock


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Consommateur pour les notifications en temps réel."""
    
    async def connect(self):
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Groupe personnel
        self.user_group = f'user_{self.user.id}'
        self.notif_group = f'notifications_{self.user.id}'
        
        # Rejoindre les groupes
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.channel_layer.group_add(self.notif_group, self.channel_name)
        await self.channel_layer.group_add('broadcast', self.channel_name)
        
        await self.accept()
        
        # Envoyer l'état initial
        await self.send_initial_state()
    
    async def disconnect(self, close_code):
        """Déconnexion."""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        if hasattr(self, 'notif_group'):
            await self.channel_layer.group_discard(self.notif_group, self.channel_name)
        await self.channel_layer.group_discard('broadcast', self.channel_name)
    
    async def receive_json(self, content):
        """Réception de message JSON du client."""
        action = content.get('action')
        
        if action == 'ping':
            await self.send_json({'type': 'pong', 'timestamp': timezone.now().isoformat()})
        
        elif action == 'mark_read':
            notification_id = content.get('notification_id')
            if notification_id:
                await self.mark_notification_read(notification_id)
        
        elif action == 'mark_all_read':
            await self.mark_all_read()
        
        elif action == 'subscribe_stock':
            product_id = content.get('product_id')
            if product_id:
                group = f'stock_{product_id}'
                await self.channel_layer.group_add(group, self.channel_name)
                await self.send_json({'type': 'subscribed', 'group': group})
        
        elif action == 'unsubscribe_stock':
            product_id = content.get('product_id')
            if product_id:
                group = f'stock_{product_id}'
                await self.channel_layer.group_discard(group, self.channel_name)
                await self.send_json({'type': 'unsubscribed', 'group': group})
    
    async def send_initial_state(self):
        """Envoie l'état initial des notifications."""
        unread_count = await self.get_unread_count()
        recent = await self.get_recent_notifications(10)
        
        await self.send_json({
            'type': 'initial_state',
            'unread_count': unread_count,
            'recent_notifications': recent,
        })
    
    # Handlers pour les messages du serveur
    
    async def notification_message(self, event):
        """Nouvelle notification."""
        await self.send_json({
            'type': 'notification',
            'notification': event['notification'],
        })
    
    async def notification_read(self, event):
        """Notification marquée comme lue."""
        await self.send_json({
            'type': 'notification_read',
            'notification_id': event['notification_id'],
        })
    
    async def unread_count_update(self, event):
        """Mise à jour du compteur."""
        await self.send_json({
            'type': 'unread_count',
            'count': event['count'],
        })
    
    async def stock_update(self, event):
        """Mise à jour de stock."""
        await self.send_json({
            'type': 'stock_update',
            'product_id': event['product_id'],
            'data': event['data'],
        })
    
    async def low_stock_alert(self, event):
        """Alerte stock bas."""
        await self.send_json({
            'type': 'low_stock_alert',
            'alert': event['alert'],
        })
    
    async def broadcast_message(self, event):
        """Message broadcast."""
        await self.send_json({
            'type': 'broadcast',
            'message': event['message'],
            'level': event.get('level', 'info'),
        })
    
    # Méthodes de base de données
    
    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(
            recipient=self.user,
            is_read=False,
            is_deleted=False,
        ).count()
    
    @database_sync_to_async
    def get_recent_notifications(self, limit=10):
        notifications = Notification.objects.filter(
            recipient=self.user,
            is_deleted=False,
        ).order_by('-created_at')[:limit]
        
        return [{
            'id': str(n.id),
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'priority': n.priority,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
        } for n in notifications]
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user,
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_all_read(self):
        return Notification.objects.filter(
            recipient=self.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())


class StockUpdateConsumer(AsyncJsonWebsocketConsumer):
    """Consommateur pour les mises à jour de stock en temps réel."""
    
    async def connect(self):
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Groupes
        self.stock_group = 'stock_updates'
        self.warehouse_group = None
        
        # Rejoindre le groupe global
        await self.channel_layer.group_add(self.stock_group, self.channel_name)
        
        # Rejoindre le groupe de l'entrepôt si spécifié
        warehouse_id = self.scope.get('query_string', b'').decode()
        if 'warehouse=' in warehouse_id:
            w_id = warehouse_id.split('warehouse=')[1].split('&')[0]
            self.warehouse_group = f'warehouse_{w_id}'
            await self.channel_layer.group_add(self.warehouse_group, self.channel_name)
        
        await self.accept()
        await self.send_json({
            'type': 'connected',
            'message': 'Connecté aux mises à jour de stock',
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.stock_group, self.channel_name)
        if self.warehouse_group:
            await self.channel_layer.group_discard(self.warehouse_group, self.channel_name)
    
    async def receive_json(self, content):
        action = content.get('action')
        
        if action == 'subscribe_product':
            product_id = content.get('product_id')
            if product_id:
                group = f'product_{product_id}'
                await self.channel_layer.group_add(group, self.channel_name)
                await self.send_json({'type': 'subscribed', 'product_id': product_id})
    
    # Handlers
    async def stock_update(self, event):
        await self.send_json({
            'type': 'stock_update',
            'update': event['update'],
            'timestamp': timezone.now().isoformat(),
        })
    
    async def low_stock_alert(self, event):
        await self.send_json({
            'type': 'low_stock_alert',
            'alert': event['alert'],
        })
    
    async def stock_movement(self, event):
        await self.send_json({
            'type': 'stock_movement',
            'movement': event['movement'],
        })