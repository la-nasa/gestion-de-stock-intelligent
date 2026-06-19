from django.urls import path
from api.v1.views.qr_views import (
    QRGenerateView,
    BarcodeGenerateView,
    QRScanView,
    QRBulkPrintView,
    ProductQRCodesView,
)

urlpatterns = [
    path('products/<uuid:product_id>/qr/generate/', QRGenerateView.as_view(), name='qr-generate'),
    path('products/<uuid:product_id>/barcode/generate/', BarcodeGenerateView.as_view(), name='barcode-generate'),
    path('products/<uuid:product_id>/codes/', ProductQRCodesView.as_view(), name='product-codes'),
    path('qr/scan/', QRScanView.as_view(), name='qr-scan'),
    path('qr/bulk-print/', QRBulkPrintView.as_view(), name='qr-bulk-print'),
]