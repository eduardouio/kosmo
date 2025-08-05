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

from trade.models import Payment, PaymentDetail


class PaymentPDFView(LoginRequiredMixin, View):

    def get(self, request, pk):
        """Generar PDF del comprobante de pago en formato compacto"""
        payment = get_object_or_404(Payment, pk=pk)

        # Obtener detalles del pago
        payment_details = PaymentDetail.objects.filter(
            payment=payment
        ).select_related('invoice', 'invoice__partner').order_by('invoice__num_invoice')

        # Crear el PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        story = []

        # Colores del tema (mismo que invoice.html)
        orange_color = colors.HexColor('#fb923c')  # Naranja principal
        green_color = colors.HexColor('#10b981')   # Verde para acentos
        red_color = colors.HexColor('#dc2626')     # Rojo para números
        gray_color = colors.HexColor('#6b7280')    # Gris para texto secundario

        # Estilos compactos
        styles = getSampleStyleSheet()

        # Estilo para el logo/header
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=10,
            textColor=orange_color
        )

        # Estilo para números importantes
        number_style = ParagraphStyle(
            'NumberStyle',
            parent=styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT,
            textColor=red_color
        )

        # Estilo para secciones
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=5,
            textColor=gray_color
        )

        # Estilo para texto normal compacto
        normal_compact = ParagraphStyle(
            'NormalCompact',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=2
        )

        # HEADER - Logo y Título (similar a invoice.html)
        header_data = [
            [
                Paragraph("KOSMO FLOWERS", header_style),
                Paragraph("COMPROBANTE DE PAGO", header_style)
            ],
            [
                Paragraph(
                    "Roses Grown by: KOSMO FLOWERS<br/>Address: Tupigachi - Tabacundo", normal_compact),
                Paragraph(
                    f"<b>No. {payment.payment_number or payment.id}</b><br/>{payment.date.strftime('%d/%m/%Y')}", number_style)
            ]
        ]

        header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 2, orange_color),
            ('INNERGRID', (0, 0), (-1, -1), 1, orange_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        # INFORMACIÓN DEL PAGO (2 columnas)
        payment_info_left = [
            f"<b>Método de Pago:</b> {payment.get_method_display()}",
            f"<b>Estado:</b> {payment.get_status_display()}",
            f"<b>Tipo:</b> {payment.get_type_transaction_display()}",
        ]

        payment_info_right = [
            f"<b>Monto Total:</b> ${payment.amount:,.2f}",
            f"<b>Fecha:</b> {payment.date.strftime('%d/%m/%Y')}",
            ""  # Espacio para balance
        ]

        # Agregar información bancaria si existe
        if payment.bank:
            payment_info_left.append(f"<b>Banco:</b> {payment.bank}")
        if payment.nro_account:
            payment_info_left.append(f"<b>Cuenta:</b> {payment.nro_account}")
        if payment.nro_operation:
            payment_info_right.append(
                f"<b>Operación:</b> {payment.nro_operation}")

        # Balancear las listas
        while len(payment_info_left) < len(payment_info_right):
            payment_info_left.append("")
        while len(payment_info_right) < len(payment_info_left):
            payment_info_right.append("")

        payment_info_data = []
        for left, right in zip(payment_info_left, payment_info_right):
            payment_info_data.append([
                Paragraph(left, normal_compact),
                Paragraph(right, normal_compact)
            ])

        payment_info_table = Table(
            payment_info_data, colWidths=[3.5*inch, 3.5*inch])
        payment_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 2, orange_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(payment_info_table)
        story.append(Spacer(1, 10))

        # FACTURAS PAGADAS (tabla compacta)
        if payment_details:
            # Encabezado de facturas
            story.append(
                Paragraph(f"FACTURAS PAGADAS ({len(payment_details)})", section_style))

            # Datos de la tabla
            invoice_data = [
                ["PROVEEDOR", "FACTURA", "FECHA", "MONTO"]
            ]

            total_invoices_amount = 0
            for detail in payment_details:
                invoice_data.append([
                    detail.invoice.partner.name[:25] + "..." if len(
                        detail.invoice.partner.name) > 25 else detail.invoice.partner.name,
                    detail.invoice.num_invoice,
                    detail.invoice.date.strftime("%d/%m/%Y"),
                    f"${detail.amount:,.2f}"
                ])
                total_invoices_amount += detail.amount

            # Fila de total
            invoice_data.append([
                "TOTAL PAGADO:",
                "",
                "",
                f"${total_invoices_amount:,.2f}"
            ])

            invoice_table = Table(invoice_data, colWidths=[
                                  3*inch, 1.5*inch, 1*inch, 1.5*inch])
            invoice_table.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), orange_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

                # Datos
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 8),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),

                # Fila total
                ('BACKGROUND', (0, -1), (-1, -1), green_color),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                ('ALIGN', (3, -1), (3, -1), 'RIGHT'),

                # Bordes y espaciado
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(invoice_table)
            story.append(Spacer(1, 10))

        # COMPROBANTE ADJUNTO (si existe)
        if payment.document:
            story.append(Paragraph("COMPROBANTE ADJUNTO", section_style))

            # Crear tabla para el comprobante
            try:
                document_path = payment.document.path
                if os.path.exists(document_path) and payment.document.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # Imagen compacta
                    img = Image(document_path)
                    img.drawHeight = 1.5*inch  # Más pequeña
                    img.drawWidth = 2*inch     # Más pequeña

                    document_data = [
                        ["IMAGEN DEL COMPROBANTE"],
                        [img]
                    ]
                else:
                    document_data = [
                        ["DOCUMENTO ADJUNTO"],
                        [f"Archivo: {payment.document.name}"]
                    ]

                document_table = Table(document_data, colWidths=[7*inch])
                document_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), gray_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                story.append(document_table)
                story.append(Spacer(1, 10))

            except Exception:
                # Si hay error con la imagen, mostrar solo texto
                story.append(
                    Paragraph(f"Documento adjunto: {payment.document.name}", normal_compact))
                story.append(Spacer(1, 10))

        # PIE DE PÁGINA compacto
        footer_data = [
            [
                "KOSMO FLOWERS - COMPROBANTE DE PAGO",
                f"Generado: {payment.date.strftime('%d/%m/%Y')}"
            ]
        ]

        footer_table = Table(footer_data, colWidths=[5*inch, 2*inch])
        footer_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), gray_color),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LINEABOVE', (0, 0), (-1, -1), 1, green_color),
        ]))
        story.append(footer_table)

        # Construir el PDF
        doc.build(story)

        # Preparar la respuesta
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="comprobante_pago_{payment.payment_number or payment.id}.pdf"'

        return response
