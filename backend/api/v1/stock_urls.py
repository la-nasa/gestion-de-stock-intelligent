from django.urls import path
from api.v1.views.stock_views import (
    StockListView, StockDetailView,
    StockMovementListView, StockMovementValidateView,
    StockEntryListView, StockEntryDetailView,
    StockOutputListView, TransferListView
)

urlpatterns = [
    # Stocks
    path('stocks/', StockListView.as_view(), name='stocks-list'),
    path('stocks/<uuid:pk>/', StockDetailView.as_view(), name='stocks-detail'),
    
    # Mouvements
    path('movements/', StockMovementListView.as_view(), name='movements-list'),
    path('movements/<uuid:pk>/validate/', StockMovementValidateView.as_view(), name='movements-validate'),
    
    # Entrées
    path('stock-entries/', StockEntryListView.as_view(), name='stock-entries-list'),
    path('stock-entries/<uuid:pk>/', StockEntryDetailView.as_view(), name='stock-entries-detail'),
    
    # Sorties
    path('stock-outputs/', StockOutputListView.as_view(), name='stock-outputs-list'),
    
    # Transferts
    path('transfers/', TransferListView.as_view(), name='transfers-list'),
]
