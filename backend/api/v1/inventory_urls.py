from django.urls import path
from api.v1.views.inventory_views import (
    InventoryListView,
    InventoryDetailView,
    InventoryLineUpdateView,
    InventoryValidateView,
)

urlpatterns = [
    path('inventories/', InventoryListView.as_view(), name='inventories-list'),
    path('inventories/<uuid:pk>/', InventoryDetailView.as_view(), name='inventories-detail'),
    path('inventories/<uuid:pk>/start/', InventoryDetailView.as_view(), name='inventories-start'),
    path('inventories/<uuid:pk>/validate/', InventoryValidateView.as_view(), name='inventories-validate'),
    path('inventories/<uuid:inventory_id>/lines/<uuid:line_id>/', InventoryLineUpdateView.as_view(), name='inventories-line-update'),
]