from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import os
import urllib.request

from trade.models import Payment, PaymentDetail


class CollectionPDFView(LoginRequiredMixin, View):

    def get(self, request, pk):
        """Generar PDF del comprobante de cobro en formato compacto"""
        collection = get_object_or_404(
            Payment, pk=pk, type_transaction='INGRESO')

        # Obtener detalles del cobro
        collection_details = PaymentDetail.objects.filter(
            payment=collection
        ).select_related('invoice', 'invoice__partner').order_by('invoice__num_invoice')

        # Crear el PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=0.3*inch,
            bottomMargin=0.3*inch,
            leftMargin=0.5*inch,
            rightMargin=0.3*inch
        )
        story = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            spaceAfter=0.1*inch,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        )

        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=0.15*inch,
            spaceAfter=0.1*inch,
            textColor=colors.HexColor('#34495e')
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=0.05*inch
        )

        bold_style = ParagraphStyle(
            'CustomBold',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=0.05*inch,
            fontName='Helvetica-Bold'
        )

        # Logo y título
        try:
            logo_path = os.path.join(os.path.dirname(
                __file__), '../../static/img/logo-kosmo.png')
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=1.5*inch, height=0.7*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 0.1*inch))
        except Exception:
            pass

        # Título principal
        title = Paragraph("COMPROBANTE DE COBRO", title_style)
        story.append(title)
        story.append(Spacer(1, 0.2*inch))

        # Información del cobro
        collection_info_data = [
            ['Número de Cobro:',
                collection.payment_number or f"C-{collection.id}"],
            ['Fecha del Cobro:', collection.date.strftime('%d/%m/%Y')],
            ['Estado:', collection.get_status_display()],
            ['Monto Total:', f"$ {collection.amount:,.2f}"],
            ['Método de Cobro:', collection.get_method_display()],
        ]

        if collection.due_date:
            collection_info_data.append(
                ['Fecha de Vencimiento:', collection.due_date.strftime('%d/%m/%Y')])

        if collection.bank:
            collection_info_data.append(['Banco:', collection.bank])

        if collection.nro_account:
            collection_info_data.append(
                ['Nro. de Cuenta:', collection.nro_account])

        if collection.nro_operation:
            collection_info_data.append(
                ['Nro. de Operación:', collection.nro_operation])

        # Tabla de información del cobro
        collection_table = Table(collection_info_data,
                                 colWidths=[2.5*inch, 3*inch])
        collection_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ]))

        story.append(collection_table)
        story.append(Spacer(1, 0.3*inch))

        # Facturas cobradas
        if collection_details.exists():
            header = Paragraph("FACTURAS COBRADAS", header_style)
            story.append(header)

            # Encabezados de la tabla de facturas
            invoices_data = [['Cliente', 'Factura', 'Monto Cobrado']]

            total_applied = 0
            for detail in collection_details:
                invoices_data.append([
                    # Truncar nombre largo
                    detail.invoice.partner.name[:30],
                    detail.invoice.num_invoice,
                    f"$ {detail.amount:,.2f}"
                ])
                total_applied += detail.amount

            # Fila de total
            invoices_data.append(
                ['', 'TOTAL APLICADO:', f"$ {total_applied:,.2f}"])

            # Crear tabla de facturas
            invoices_table = Table(invoices_data, colWidths=[
                                   2.5*inch, 1.5*inch, 1.5*inch])
            invoices_table.setStyle(TableStyle([
                # Encabezados
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

                # Datos
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
                ('ALIGN', (0, 1), (1, -2), 'LEFT'),
                ('ALIGN', (2, 1), (2, -2), 'RIGHT'),

                # Fila de total
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 10),
                ('ALIGN', (0, -1), (1, -1), 'RIGHT'),
                ('ALIGN', (2, -1), (2, -1), 'RIGHT'),

                # Estilos generales
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ]))

            story.append(invoices_table)
            story.append(Spacer(1, 0.2*inch))

        # Información adicional
        if collection.processed_by or collection.approved_by:
            story.append(Spacer(1, 0.2*inch))

            additional_info = []

            if collection.processed_by:
                processed_by_name = (
                    collection.processed_by.get_full_name() or
                    collection.processed_by.username
                )
                additional_info.append(['Procesado por:', processed_by_name])

            if collection.approved_by:
                approved_by_name = (
                    collection.approved_by.get_full_name() or
                    collection.approved_by.username
                )
                additional_info.append(['Aprobado por:', approved_by_name])

                if collection.approval_date:
                    additional_info.append([
                        'Fecha de Aprobación:',
                        collection.approval_date.strftime('%d/%m/%Y %H:%M')
                    ])

            if additional_info:
                additional_table = Table(
                    additional_info, colWidths=[2*inch, 3*inch])
                additional_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
                ]))

                story.append(additional_table)

        # Pie de página
        story.append(Spacer(1, 0.3*inch))

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7f8c8d')
        )

        footer_text = f"""
        <b>KOSMO FLOWERS</b><br/>
        Documento generado automáticamente el {collection.created_at.strftime('%d/%m/%Y %H:%M')}<br/>
        Este comprobante es válido como soporte de cobro
        """

        footer = Paragraph(footer_text, footer_style)
        story.append(footer)

        # Generar el PDF
        doc.build(story)
        buffer.seek(0)

        # Preparar la respuesta HTTP
        response = HttpResponse(
            buffer.getvalue(), content_type='application/pdf')
        filename = f"cobro_{collection.payment_number or collection.id}_{collection.date.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
