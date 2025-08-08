from io import BytesIO
from datetime import date
from django.http import HttpResponse
from django.views import View
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from django.utils.formats import number_format

from .PartnerAccountStatmentView import PartnerAccountStatmentView


class PartnerAccountStatmentPDF(View):
    """Genera PDF del estado de cuenta reutilizando el contexto existente."""

    def get(self, request, *args, **kwargs):
        # Reutilizar la view original para obtener los datos
        base_view = PartnerAccountStatmentView()
        base_view.request = request
        ctx = base_view.get_context_data()

        if ctx.get('missing_partner') or ctx.get('partner_not_found'):
            return HttpResponse(
                'Debe seleccionar un cliente válido.', status=400
            )

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        top = height - 30 * mm

        partner = ctx['partner']
        entries = ctx['entries']

        # Encabezado
        p.setFont('Helvetica-Bold', 14)
        p.drawString(20 * mm, top, 'ESTADO DE CUENTA')
        p.setFont('Helvetica', 9)
        p.drawString(20 * mm, top - 8 * mm, f'Cliente: {partner.name}')
        p.drawString(
            20 * mm,
            top - 12 * mm,
            f'Tax ID: {partner.business_tax_id or "-"}'
        )
        p.drawString(
            20 * mm,
            top - 16 * mm,
            f'Crédito: {partner.credit_term} días'
        )
        p.drawString(
            140 * mm,
            top - 8 * mm,
            f'Fecha: {date.today().strftime("%d/%m/%Y")}'
        )
        p.drawString(
            140 * mm,
            top - 12 * mm,
            f'Saldo: {number_format(ctx["net_balance"], 2)}'
        )

        # Tabla
        col_headers = [
            'Fecha', 'Documento', 'Crédito', 'Valor', 'Pago', 'Saldo', 'Ref'
        ]
        col_widths = [22, 38, 16, 22, 22, 22, 22]  # en mm
        start_y = top - 28 * mm
        x = 12 * mm

        p.setFont('Helvetica-Bold', 8)
        for i, head in enumerate(col_headers):
            p.drawString(x, start_y, head)
            x += col_widths[i] * mm
        p.setLineWidth(0.4)
        p.line(12 * mm, start_y - 2, width - 12 * mm, start_y - 2)

        p.setFont('Helvetica', 7)
        y = start_y - 6 * mm
        for e in entries:
            if y < 20 * mm:  # nueva página
                p.showPage()
                p.setFont('Helvetica-Bold', 8)
                x = 12 * mm
                for i, head in enumerate(col_headers):
                    p.drawString(x, height - 20 * mm, head)
                    x += col_widths[i] * mm
                p.line(
                    12 * mm, height - 22 * mm,
                    width - 12 * mm, height - 22 * mm
                )
                p.setFont('Helvetica', 7)
                y = height - 28 * mm

            x = 12 * mm
            fecha = e.get('date') or ''
            fecha_txt = fecha.strftime('%d/%m/%Y') if fecha else ''
            documento = e.get('document') or ''
            credito = (
                '' if e['type'] != 'INVOICE'
                else str(e.get('credit_days', ''))
            )
            valor = (
                number_format(e.get('invoice_amount') or 0, 2)
                if e['type'] == 'INVOICE' else ''
            )
            pago = ''
            if e.get('payment_amount'):
                pago = number_format(e.get('payment_amount') or 0, 2)
            saldo = (
                number_format(e.get('balance') or 0, 2)
                if e['type'] == 'INVOICE' else ''
            )
            ref = e.get('reference') or ''

            # Color para vencida o pago
            if e['type'] == 'PAYMENT':
                p.setFillColor(colors.red)
            elif ref == 'FACTURA VENCIDA':
                p.setFillColor(colors.red)
            else:
                p.setFillColor(colors.black)

            for w, text in zip(col_widths, [
                fecha_txt, documento[:18], credito,
                valor, pago, saldo, ref[:10]
            ]):
                p.drawString(x, y, text)
                x += w * mm
            y -= 5 * mm

        # Totales
        y -= 4 * mm
        p.setFillColor(colors.black)
        p.setFont('Helvetica-Bold', 8)
        total_line = (
            'TOTAL FACTURAS: ' + number_format(
                ctx['total_invoices_amount'], 2
            ) + '  PAGOS: ' + number_format(
                ctx['total_payments_amount'], 2
            ) + '  PENDIENTE: ' + number_format(
                ctx['total_pending_balance'], 2
            )
        )
        p.drawString(12 * mm, y, total_line)

        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="estado_cuenta.pdf"'
        )
        response.write(pdf)
        return response
