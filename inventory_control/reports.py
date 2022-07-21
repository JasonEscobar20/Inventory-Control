import json
import os

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse, HttpResponse

from datetime import datetime

from openpyxl import load_workbook
from openpyxl.styles.colors import BLACK
from openpyxl.styles import Border, Side

from inventory_control.models import InventoryCount


class InventoryCountReport(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        params = request.GET
        filter_data = {}
        entry_date = params.get('entry_date', '')
        end_date = params.get('end_date', '')

        for key, value in params.items():
            if value != '':
                if key == 'sku':
                    filter_data['product__sku'] = value
                if key == 'product_status':
                    filter_data['product_status'] = value
                if key == 'measurement_unit':
                    filter_data['measurement_unit'] = value
                if key == 'storage_type':
                    filter_data['storage_type'] = value

        if entry_date != '' and end_date == '':
            filter_data['entry_date'] = entry_date
        
        if entry_date != '' and end_date != '':
            filter_data['entry_date__range'] = [entry_date, end_date]

        inventory_counts = InventoryCount.objects.filter(**filter_data)

        # os.chdir('/home/admin/server')

        wb = load_workbook('core/static/assets/report_templates/report.xlsx')
        ws = wb.active
        initial_row = 13

        border =  Border(
            left=Side(style='thin',color=BLACK),
            right=Side(style='thin',color=BLACK),
            top=Side(style='thin', color=BLACK),
            bottom=Side(style='thin',  color=BLACK)
        )

        for item in inventory_counts:

            ws.cell(row=initial_row, column=1).value = item.product.sku
            ws.cell(row=initial_row, column=2).value = item.product.category.name
            ws.cell(row=initial_row, column=3).value = item.product.description
            ws.cell(row=initial_row, column=4).value = item.amount

            for column in range(1, 5):
                ws.cell(row=initial_row, column=column).border = border

            initial_row = initial_row + 1


        filename = 'Reporte de conteos.xlsx'
        response = HttpResponse(content_type='application/ms-excel')
        content = f'attachment; filename={filename}'
        response['Content-Disposition'] = content
        wb.save(response)
        return response