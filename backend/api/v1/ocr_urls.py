from django.urls import path
from api.v1.views.ocr_views import OCRInvoiceView, OCRCreateEntryView

urlpatterns = [
    path('ocr/invoice/', OCRInvoiceView.as_view(), name='ocr-invoice'),
    path('ocr/create-entry/', OCRCreateEntryView.as_view(), name='ocr-create-entry'),
]