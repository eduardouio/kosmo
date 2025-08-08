from io import BytesIO
from datetime import date
from django.http import HttpResponse
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from .PartnerAccountStatmentView import PartnerAccountStatmentView


class PartnerAccountStatmentExcel(View):
    """Exporta el estado de cuenta a Excel (xlsx)."""

    def get(self, request, *args, **kwargs):
        base_view = PartnerAccountStatmentView()
        base_view.request = request
        ctx = base_view.get_context_data()

        if ctx.get('missing_partner') or ctx.get('partner_not_found'):
            return HttpResponse(
                'Debe seleccionar un cliente válido.', status=400
            )

        wb = Workbook()
        ws = wb.active
        ws.title = 'EstadoCuenta'

        partner = ctx['partner']
        ws.append(['ESTADO DE CUENTA'])
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=7)
        ws['A1'].font = Font(size=14, bold=True)

        ws.append([
            f'Cliente: {partner.name}', '', '', '', 'Fecha',
            date.today().strftime('%d/%m/%Y')
        ])
        ws.append([
            f'Tax ID: {partner.business_tax_id or "-"}', '', '', '',
            'Saldo', ctx['net_balance']
        ])
        ws.append([f'Crédito: {partner.credit_term} días'])
        ws.append([])

        headers = [
            'Fecha', 'Documento', 'Crédito', 'Valor', 'Pago', 'Saldo',
            'Referencia'
        ]
        ws.append(headers)
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=5, column=col)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
            cell.fill = PatternFill(
                start_color='F6DFD4', end_color='F6DFD4', fill_type='solid'
            )

        row = 6
        for e in ctx['entries']:
            fecha = e.get('date')
            ws.cell(
                row=row, column=1,
                value=fecha.strftime('%d/%m/%Y') if fecha else ''
            )
            ws.cell(row=row, column=2, value=e.get('document'))
            ws.cell(
                row=row, column=3,
                value=e.get('credit_days') if e['type'] == 'INVOICE' else ''
            )
            ws.cell(
                row=row, column=4,
                value=(
                    e.get('invoice_amount') if e['type'] == 'INVOICE' else None
                )
            )
            ws.cell(
                row=row, column=5,
                value=(
                    e.get('payment_amount') if e['type'] == 'PAYMENT'
                    else (
                        e.get('payment_amount')
                        if e.get('payment_amount') else None
                    )
                )
            )
            ws.cell(
                row=row, column=6,
                value=(
                    e.get('balance') if e['type'] == 'INVOICE' else None
                )
            )
            ws.cell(row=row, column=7, value=e.get('reference'))
            row += 1

        ws.append([])
        ws.append([
            'TOTAL FACTURAS', ctx['total_invoices_amount'],
            'TOTAL PAGOS', ctx['total_payments_amount'],
            'PENDIENTE', ctx['total_pending_balance']
        ])

        response = HttpResponse(
            content_type=(
                'application/vnd.openxmlformats-officedocument.'
                'spreadsheetml.sheet'
            )
        )
        response['Content-Disposition'] = (
            'attachment; filename="estado_cuenta.xlsx"'
        )
        bio = BytesIO()
        wb.save(bio)
        bio.seek(0)
        response.write(bio.read())
        return response
