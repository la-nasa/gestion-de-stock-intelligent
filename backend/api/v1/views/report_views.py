from rest_framework import views, status
from django.http import HttpResponse
from core.utils.response import success_response, error_response
import csv, io
from openpyxl import Workbook

class ReportGenerateView(views.APIView):
    def post(self, request):
        try:
            report_type = request.data.get("type", "stock_level")
            format_type = request.data.get("format", "PDF")
            
            # Données simulées pour le rapport
            if report_type == "stock_level":
                from apps.stock_movements.models import Stock
                stocks = Stock.objects.filter(is_deleted=False).select_related("product", "warehouse")[:100]
                data = [["Produit", "Référence", "Entrepôt", "Quantité", "Prix", "Valeur"]]
                for s in stocks:
                    data.append([s.product.name, s.product.reference, s.warehouse.name, str(s.quantity), str(s.unit_price), str(s.quantity * s.unit_price)])
            elif report_type == "movements":
                from apps.stock_movements.models import StockMovement
                movements = StockMovement.objects.filter(is_deleted=False).select_related("stock__product")[:100]
                data = [["Date", "Type", "Produit", "Quantité", "Prix"]]
                for m in movements:
                    data.append([m.created_at.isoformat(), m.movement_type, m.stock.product.name, str(m.quantity), str(m.total_price)])
            elif report_type == "consumption":
                data = [["Département", "Montant"], ["Informatique", "2500000"], ["Bureautique", "1800000"], ["Laboratoire", "1200000"]]
            else:
                data = [["Données", "Valeur"], ["Exemple", "1000"]]
            
            if format_type == "CSV":
                output = io.StringIO()
                writer = csv.writer(output)
                for row in data: writer.writerow(row)
                response = HttpResponse(output.getvalue().encode("utf-8-sig"), content_type="text/csv")
                response["Content-Disposition"] = f"attachment; filename=rapport_{report_type}.csv"
                return response
            elif format_type == "EXCEL":
                wb = Workbook()
                ws = wb.active
                for row in data: ws.append(row)
                output = io.BytesIO()
                wb.save(output)
                response = HttpResponse(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response["Content-Disposition"] = f"attachment; filename=rapport_{report_type}.xlsx"
                return response
            else:
                return error_response(message="Format PDF non disponible, utilisez CSV ou EXCEL", status_code=400)
        except Exception as e:
            return error_response(message=str(e), status_code=500)

class ReportHistoryView(views.APIView):
    def get(self, request):
        return success_response(data={"results": [], "count": 0})
