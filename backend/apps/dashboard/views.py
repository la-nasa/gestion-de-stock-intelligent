"""
Vues pour le tableau de bord.
"""
from rest_framework import views
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.products.models import Product, Category
from apps.stock_movements.models import Stock, StockMovement
from apps.purchase_orders.models import PurchaseOrder
from apps.transfers.models import Transfer
from apps.suppliers.models import Supplier
from core.utils.response import success_response


class DashboardView(views.APIView):
    """Vue principale du tableau de bord."""

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # KPIs
        total_products = Product.objects.filter(is_deleted=False).count()
        
        total_stock_value = Stock.objects.filter(
            is_deleted=False
        ).aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total'] or 0
        
        pending_orders = PurchaseOrder.objects.filter(
            is_deleted=False,
            status__in=['DRAFT', 'PENDING', 'APPROVED', 'ORDERED']
        ).count()
        
        low_stock_items = Stock.objects.filter(
            is_deleted=False,
            quantity__lte=F('product__min_stock')
        ).count()
        
        active_transfers = Transfer.objects.filter(
            is_deleted=False,
            status__in=['PENDING', 'APPROVED', 'IN_TRANSIT']
        ).count()
        
        total_suppliers = Supplier.objects.filter(
            is_deleted=False,
            status='ACTIVE'
        ).count()

        # Mouvements récents
        recent_movements = StockMovement.objects.filter(
            is_deleted=False
        ).select_related(
            'stock__product', 'stock__warehouse', 'performed_by'
        ).order_by('-created_at')[:10]

        activities = []
        for mov in recent_movements:
            activities.append({
                'id': str(mov.id),
                'type': 'entry' if mov.movement_type == 'ENTRY' else 'output',
                'product': mov.stock.product.name,
                'quantity': mov.quantity,
                'user': mov.performed_by.get_full_name() if mov.performed_by else 'Système',
                'warehouse': mov.stock.warehouse.name,
                'time': self._time_ago(mov.created_at),
            })

        # Consommation mensuelle (6 derniers mois)
        monthly_consumption = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_name = month_date.strftime('%b')
            
            movements = StockMovement.objects.filter(
                is_deleted=False,
                movement_type='OUTPUT',
                created_at__year=month_date.year,
                created_at__month=month_date.month
            ).aggregate(
                total=Sum('total_price')
            )
            
            monthly_consumption.append({
                'month': month_name,
                'value': float(movements['total'] or 0),
            })

        # Stock par catégorie
        categories = Category.objects.filter(is_deleted=False)
        stock_by_category = []
        for cat in categories:
            value = Stock.objects.filter(
                is_deleted=False,
                product__category=cat
            ).aggregate(
                total=Sum(F('quantity') * F('unit_price'))
            )['total'] or 0
            
            if value > 0:
                stock_by_category.append({
                    'name': cat.name,
                    'value': float(value),
                })

        data = {
            'kpis': {
                'totalProducts': total_products,
                'stockValue': float(total_stock_value),
                'pendingOrders': pending_orders,
                'lowStockItems': low_stock_items,
                'activeTransfers': active_transfers,
                'totalSuppliers': total_suppliers,
            },
            'monthlyConsumption': monthly_consumption,
            'stockByCategory': stock_by_category[:6],
            'recentActivities': activities,
        }

        return success_response(data=data)

    def _time_ago(self, dt):
        """Formate le temps écoulé."""
        now = timezone.now()
        diff = now - dt
        
        if diff.days > 30:
            return f"Il y a {diff.days // 30} mois"
        elif diff.days > 0:
            return f"Il y a {diff.days}j"
        elif diff.seconds > 3600:
            return f"Il y a {diff.seconds // 3600}h"
        elif diff.seconds > 60:
            return f"Il y a {diff.seconds // 60}min"
        else:
            return "À l'instant"


from django.db.models import F
