"""Vues pour la génération de rapports."""
from rest_framework import views
from django.http import HttpResponse
from services.report_service import ReportService
from api.v1.permissions import IsManager
from core.utils.response import success_response, error_response


class ReportGenerateView(views.APIView):
    """Génération de rapport."""
    
    permission_classes = [IsManager]
    
    def post(self, request):
        report_type = request.data.get('type', 'stock_level')
        format_type = request.data.get('format', 'PDF')
        filters = request.data.get('filters', {})
        
        try:
            if report_type == 'stock_level':
                content = ReportService.generate_stock_level_report(format_type, filters)
                filename = f'rapport_stock.{format_type.lower()}'
            elif report_type == 'movements':
                content = ReportService.generate_movement_report(format_type, filters)
                filename = f'rapport_mouvements.{format_type.lower()}'
            elif report_type == 'consumption':
                content = ReportService.generate_consumption_report(format_type, filters)
                filename = f'rapport_consommation.{format_type.lower()}'
            elif report_type == 'inventory':
                inventory_id = request.data.get('inventory_id')
                if not inventory_id:
                    return error_response(message="ID inventaire requis", status_code=400)
                content = ReportService.generate_inventory_report(inventory_id, format_type)
                filename = f'rapport_inventaire.{format_type.lower()}'
            else:
                return error_response(message=f"Type de rapport inconnu: {report_type}", status_code=400)
            
            # Déterminer le content type
            content_types = {
                'PDF': 'application/pdf',
                'EXCEL': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'CSV': 'text/csv',
            }
            
            response = HttpResponse(
                content,
                content_type=content_types.get(format_type, 'application/octet-stream')
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            return error_response(message=str(e), status_code=500)


class ReportHistoryView(views.APIView):
    """Historique des rapports générés."""
    
    permission_classes = [IsManager]
    
    def get(self, request):
        from apps.reports.models import Report
        
        reports = Report.objects.filter(is_deleted=False).order_by('-created_at')[:50]
        
        data = [{
            'id': str(r.id),
            'name': r.name,
            'reference': r.reference,
            'type': r.type,
            'format': r.format,
            'status': r.status,
            'file_size': r.file_size,
            'created_at': r.created_at.isoformat(),
            'generated_by': r.generated_by.get_full_name() if r.generated_by else '',
        } for r in reports]
        
        return success_response(data={'results': data, 'count': len(data)})