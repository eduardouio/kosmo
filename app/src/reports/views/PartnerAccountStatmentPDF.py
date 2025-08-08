from io import BytesIO
from datetime import date
import os
import unicodedata
from django.http import HttpResponse
from django.views import View
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from django.utils.formats import number_format
from django.conf import settings

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
        partner = ctx['partner']
        entries = ctx['entries']

        ORANGE = HexColor('#d86f23')
        SOFT = HexColor('#f6dfd4')

        def draw_logo(_p):
            # Intentar varios paths
            logo_candidates = [
                os.path.join(
                    settings.BASE_DIR, 'static', 'img', 'logo-kosmo.png'
                ),
                os.path.join(
                    settings.BASE_DIR, 'static', 'img', 'logo.png'
                ),
                os.path.join(
                    settings.BASE_DIR, 'static', 'img', 'logo-bg.png'
                ),
            ]
            for lp in logo_candidates:
                if os.path.exists(lp):
                    try:
                        _p.drawImage(
                            lp, 15 * mm, height - 40 * mm,
                            width=70 * mm, preserveAspectRatio=True,
                            mask='auto'
                        )
                        break
                    except Exception:
                        continue

        def draw_page_header(_p, show_partner_box=False):
            top_y = height - 6 * mm
            box_w = 60 * mm
            box_h = 14 * mm
            x_box = width - box_w - 10 * mm
            y_box = top_y - box_h
            _p.setStrokeColor(ORANGE)
            _p.setLineWidth(1)
            _p.setFillColor(colors.white)
            _p.rect(x_box, y_box, box_w, box_h, stroke=1, fill=0)
            _p.line(x_box, y_box + box_h - 6 * mm, x_box + box_w, y_box + box_h - 6 * mm)
            _p.line(x_box + 24 * mm, y_box, x_box + 24 * mm, y_box + 6 * mm)
            _p.setFillColor(colors.black)
            _p.setFont('Helvetica-Bold', 9)
            _p.drawCentredString(x_box + box_w / 2, y_box + box_h - 5 * mm, 'ESTADO DE CUENTA')
            _p.setFont('Helvetica-Bold', 7)
            _p.drawCentredString(x_box + 12 * mm, y_box + 1.5 * mm, 'FECHA')
            _p.setFont('Helvetica', 7)
            _p.drawCentredString(
                x_box + (box_w - 24 * mm)/2 + 24 * mm,
                y_box + 1.5 * mm,
                date.today().strftime('%d/%m/%y')
            )
            draw_logo(_p)
            if show_partner_box:
                box_x = 10 * mm
                box_w2 = width - 20 * mm
                box_h2 = 42 * mm
                box_y = y_box - 4 * mm - box_h2
                _p.setStrokeColor(ORANGE)
                _p.setLineWidth(1)
                _p.roundRect(box_x, box_y, box_w2, box_h2, 5 * mm, stroke=1, fill=0)
                _p.setFont('Helvetica-Bold', 11)
                _p.drawCentredString(box_x + box_w2 / 2, box_y + box_h2 - 7 * mm, partner.name.upper())
                _p.setFont('Helvetica', 7)
                info_y = box_y + box_h2 - 13 * mm
                lines = [
                    f'E-mail: {partner.email or ""}',
                    f'Tax ID: {partner.business_tax_id or ""}',
                    f'Crédito: {partner.credit_term} días'
                ]
                for ln in lines:
                    _p.drawString(box_x + 4 * mm, info_y, ln)
                    info_y -= 5 * mm
                band_y = box_y + 11 * mm
                _p.line(box_x, band_y, box_x + box_w2, band_y)
                saldo_txt = number_format(ctx['net_balance'], 2)
                _p.setFont('Helvetica-Bold', 9)
                _p.drawString(box_x + 5 * mm, band_y - 5 * mm, 'ESTADO DE CUENTA')
                _p.drawRightString(box_x + box_w2 - 5 * mm, band_y - 5 * mm, saldo_txt)
                return box_y
            return y_box - 2 * mm

        top_ref = draw_page_header(p, show_partner_box=True)
        # Tabla -----------------------------------------------------------------
        col_headers = [
            'FECHA', 'DOCUMENTO', 'TIEMPO CREDITO',
            'VALOR', 'PAGO', 'SALDO', 'REFERENCIA'
        ]
        col_widths = [22, 34, 24, 24, 24, 24, 32]  # mm
        # top_ref es la base (y inferior) del recuadro del partner.
        # Antes se restaban 50mm generando un gran espacio en blanco.
        # Usamos sólo 12mm como margen para acercar la tabla al header.
        start_y = top_ref - 12 * mm

        def draw_table_header(y_pos):
            p.setFillColor(SOFT)
            p.rect(
                12 * mm, y_pos - 5 * mm,
                sum(col_widths) * mm, 6 * mm,
                fill=1, stroke=0
            )
            p.setFillColor(colors.black)
            p.setFont('Helvetica-Bold', 7)
            xc = 12 * mm + 2
            for i, head in enumerate(col_headers):
                p.drawString(xc, y_pos - 3.2 * mm, head)
                xc += col_widths[i] * mm
            p.setFont('Helvetica', 6.8)

        draw_table_header(start_y)
        y = start_y - 7 * mm

        for e in entries:
            if y < 18 * mm:  # salto página
                p.showPage()
                draw_page_header(p, show_partner_box=False)
                draw_table_header(height - 20 * mm)
                y = height - 27 * mm

            x = 12 * mm + 1
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
            pago = (
                number_format(e.get('payment_amount') or 0, 2)
                if e.get('payment_amount') else ''
            )
            saldo = (
                number_format(e.get('balance') or 0, 2)
                if e['type'] == 'INVOICE' else ''
            )
            ref = e.get('reference') or ''

            # Fondo fila
            p.setFillColor(colors.white if e['type'] == 'INVOICE' else HexColor('#ffecec'))
            p.rect(12 * mm, y - 1.8 * mm, sum(col_widths) * mm, 5.2 * mm, fill=1, stroke=0)
            # Texto en columnas
            for w, text, style in zip(
                col_widths,
                [
                    fecha_txt, documento[:18], credito,
                    valor, pago, saldo, ref[:18]
                ],
                ['n', 'n', 'c', 'r', 'r', 'r', 'n']
            ):
                p.setFillColor(
                    colors.red if (
                        'VENCIDA' in ref or e['type'] == 'PAYMENT'
                    ) and style != 'c' else colors.black
                )
                if style == 'r':
                    p.drawRightString(x + w * mm - 2, y, text)
                elif style == 'c':
                    p.drawCentredString(x + (w * mm)/2, y, text)
                else:
                    p.drawString(x, y, text)
                x += w * mm
            y -= 5.4 * mm

        # Totales
        y -= 3 * mm
        p.setFillColor(colors.black)
        p.setFont('Helvetica-Bold', 7.5)
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

        # Nombre de archivo dinámico con el nombre del partner
        def slugify(value: str) -> str:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
            value = value.lower().replace(' ', '_')
            return ''.join(c for c in value if c.isalnum() or c in ('_', '-')) or 'partner'

        filename = f"estado_cuenta_{slugify(partner.name)}.pdf"
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        return response
