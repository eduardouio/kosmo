from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO

from trade.models import Payment, PaymentDetail


class PaymentPDFView(LoginRequiredMixin, View):

    def get(self, request, pk):
        """Generar PDF del comprobante de pago"""
        payment = get_object_or_404(Payment, pk=pk)

        # Obtener detalles del pago
        payment_details = PaymentDetail.objects.filter(
            payment=payment
        ).select_related(
            'invoice', 'invoice__partner'
        ).order_by('invoice__num_invoice')

        # Crear el PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        # Estilos
        styles = getSampleStyleSheet()

        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#2c3e50')
        )

        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#34495e')
        )

        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=5
        )

        # Estilo para texto centrado
        center_style = ParagraphStyle(
            'CustomCenter',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=5
        )

        # Título del documento
        story.append(Paragraph("COMPROBANTE DE PAGO", title_style))
        story.append(Spacer(1, 20))

        # Información de la empresa (opcional)
        company_info = [
            ["KOSMO FLOWERS", ""],
            ["Comprobante de Pago Nº:",
                f"{payment.payment_number or payment.id}"],
            ["Fecha de emisión:", payment.date.strftime("%d/%m/%Y")],
        ]

        company_table = Table(company_info, colWidths=[3*inch, 3*inch])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(company_table)
        story.append(Spacer(1, 20))

        # Información del pago
        story.append(Paragraph("INFORMACIÓN DEL PAGO", subtitle_style))

        payment_info_data = [
            ["Número de Pago:", payment.payment_number or "Sin número asignado"],
            ["Fecha del Pago:", payment.date.strftime("%d/%m/%Y")],
            ["Tipo de Transacción:", payment.get_type_transaction_display()],
            ["Método de Pago:", payment.get_method_display()],
            ["Estado:", payment.get_status_display()],
            ["Monto Total:", f"${payment.amount:,.2f}"],
        ]

        if payment.due_date:
            payment_info_data.insert(-1, ["Fecha de Vencimiento:",
                                     payment.due_date.strftime("%d/%m/%Y")])

        payment_info_table = Table(
            payment_info_data, colWidths=[2*inch, 4*inch])
        payment_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ]))
        story.append(payment_info_table)
        story.append(Spacer(1, 15))

        # Información bancaria (si existe)
        if payment.bank or payment.nro_account or payment.nro_operation:
            story.append(Paragraph("INFORMACIÓN BANCARIA", subtitle_style))

            bank_info_data = []
            if payment.bank:
                bank_info_data.append(["Banco:", payment.bank])
            if payment.nro_account:
                bank_info_data.append(
                    ["Número de Cuenta:", payment.nro_account])
            if payment.nro_operation:
                bank_info_data.append(
                    ["Número de Operación:", payment.nro_operation])

            bank_info_table = Table(bank_info_data, colWidths=[2*inch, 4*inch])
            bank_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ]))
            story.append(bank_info_table)
            story.append(Spacer(1, 15))

        # Facturas pagadas
        if payment_details:
            story.append(
                Paragraph(f"FACTURAS PAGADAS ({len(payment_details)})", subtitle_style))

            # Encabezados de la tabla de facturas
            invoice_data = [
                ["Proveedor", "Núm. Factura", "Fecha Factura", "Monto Pagado"]
            ]

            total_invoices_amount = 0
            for detail in payment_details:
                invoice_data.append([
                    detail.invoice.partner.name,
                    detail.invoice.num_invoice,
                    detail.invoice.date.strftime("%d/%m/%Y"),
                    f"${detail.amount:,.2f}"
                ])
                total_invoices_amount += detail.amount

            # Fila de total
            invoice_data.append([
                "TOTAL FACTURAS:",
                "",
                "",
                f"${total_invoices_amount:,.2f}"
            ])

            invoice_table = Table(invoice_data, colWidths=[
                                  2.5*inch, 1.5*inch, 1*inch, 1*inch])
            invoice_table.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

                # Datos
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
                ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),

                # Fila total
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 10),

                # Bordes
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(invoice_table)
            story.append(Spacer(1, 15))

        # Comprobante adjunto (si existe)
        if payment.document:
            story.append(Paragraph("COMPROBANTE ADJUNTO", subtitle_style))

            try:
                # Información sobre el documento
                document_name = payment.document.name
                story.append(
                    Paragraph(f"Archivo: {document_name}", normal_style))

                # Intentar agregar la imagen solo si es válida
                document_path = payment.document.path
                if os.path.exists(document_path):
                    if document_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        try:
                            img = Image(document_path)
                            # Redimensionar imagen para que quepa en el PDF
                            img_width = 4*inch
                            img_height = 3*inch
                            img.drawHeight = img_height
                            img.drawWidth = img_width
                            story.append(img)
                        except Exception as img_error:
                            story.append(Paragraph(
                                f"Imagen no disponible: {str(img_error)}",
                                normal_style
                            ))
                    else:
                        story.append(Paragraph(
                            "Documento PDF adjunto disponible",
                            normal_style
                        ))
                else:
                    story.append(Paragraph(
                        "Documento no encontrado en el servidor",
                        normal_style
                    ))
            except Exception as e:
                story.append(Paragraph(
                    f"Error al procesar documento: {str(e)}",
                    normal_style
                ))

            story.append(Spacer(1, 15))

        # Información de procesamiento
        if payment.processed_by or payment.approved_by:
            story.append(
                Paragraph("INFORMACIÓN DE PROCESAMIENTO", subtitle_style))

            process_info_data = []
            if payment.processed_by:
                process_info_data.append([
                    "Procesado por:",
                    payment.processed_by.get_full_name() or payment.processed_by.username
                ])

            if payment.approved_by:
                process_info_data.append([
                    "Aprobado por:",
                    payment.approved_by.get_full_name() or payment.approved_by.username
                ])
                if payment.approval_date:
                    process_info_data.append([
                        "Fecha de aprobación:",
                        payment.approval_date.strftime("%d/%m/%Y %H:%M")
                    ])

            if process_info_data:
                process_info_table = Table(
                    process_info_data, colWidths=[2*inch, 4*inch])
                process_info_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ]))
                story.append(process_info_table)
                story.append(Spacer(1, 15))

        # Pie de página
        story.append(Spacer(1, 30))
        story.append(Paragraph("_" * 50, center_style))
        story.append(Paragraph("Firma Autorizada", center_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            f"Documento generado el {payment.date.strftime('%d/%m/%Y')}", center_style))

        # Construir el PDF
        doc.build(story)

        # Preparar la respuesta
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="comprobante_pago_{payment.payment_number or payment.id}.pdf"'

        return response
