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
from reportlab.lib.enums import TA_LEFT
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

        # Colores del tema (verde para cobros)
        green_color = colors.HexColor('#10b981')   # Verde principal
        orange_color = colors.HexColor('#fb923c')  # Naranja para acentos
        gray_color = colors.HexColor('#6b7280')    # Gris texto secundario

        # Estilos compactos
        styles = getSampleStyleSheet()

        # Estilo para el logo/header (fuente más pequeña)
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=5,
            textColor=green_color
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

        # HEADER - Logo y Título (con logo de Kosmo)
        temp_logo_path = None
        try:
            # Intentar cargar el logo de Kosmo
            logo_url = "https://app.kosmoflowers.com/static/img/logo-kosmo.png"
            temp_logo_path = "/tmp/kosmo_logo.png"

            # Descargar el logo temporalmente
            urllib.request.urlretrieve(logo_url, temp_logo_path)

            # Crear imagen del logo con proporción correcta
            logo_img = Image(temp_logo_path)
            logo_img.drawHeight = 0.7*inch
            logo_img.drawWidth = 1.8*inch

            # Crear tabla con logo y texto
            logo_content = Table([
                [logo_img]
            ], colWidths=[5*inch])
            logo_content.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))

        except Exception:
            # Si falla la descarga, usar solo texto
            logo_content = Paragraph("🌹 KOSMO FLOWERS", header_style)

        header_data = [
            [
                logo_content,
                Paragraph(
                    f"COMPROBANTE DE COBRO <br/> No. {collection.payment_number or collection.id}<br/>"
                    f"{collection.date.strftime('%d/%m/%Y')}", header_style)
            ]
        ]

        header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 0.25, green_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, green_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        # INFORMACIÓN DEL COBRO (tabla estructurada)
        collection_info_data = [
            ["Método de Cobro:", collection.get_method_display(), "Monto Total:",
             f"${collection.amount:,.2f}"],
            ["Estado:", collection.get_status_display(), "Fecha:",
             collection.date.strftime('%d/%m/%Y')],
            ["Tipo:", collection.get_type_transaction_display(), "Banco:",
             collection.bank or ""],
            ["Operación:", collection.nro_operation or "", "Cuenta:",
             collection.nro_account or ""],
        ]

        collection_info_table = Table(
            collection_info_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
        collection_info_table.setStyle(TableStyle([
            # Etiquetas en negrita (columnas 0 y 2)
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), gray_color),
            ('TEXTCOLOR', (2, 0), (2, -1), gray_color),

            # Valores (columnas 1 y 3)
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),

            # Alineación
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Bordes y espaciado
            ('BOX', (0, 0), (-1, -1), 0.25, green_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, green_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(collection_info_table)
        story.append(Spacer(1, 10))

        # FACTURAS COBRADAS (tabla compacta)
        if collection_details:
            # Encabezado de facturas
            story.append(
                Paragraph(f"FACTURAS COBRADAS ({len(collection_details)})", section_style))

            # Datos de la tabla
            invoice_data = [
                ["CLIENTE", "FACTURA", "FECHA", "MONTO"]
            ]

            total_invoices_amount = 0
            for detail in collection_details:
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
                "TOTAL COBRADO:",
                "",
                "",
                f"${total_invoices_amount:,.2f}"
            ])

            invoice_table = Table(invoice_data, colWidths=[
                                  3*inch, 1.5*inch, 1*inch, 1.5*inch])
            invoice_table.setStyle(TableStyle([
                # Encabezado - texto con color en lugar de fondo
                ('TEXTCOLOR', (0, 0), (-1, 0), green_color),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

                # Datos
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 8),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),

                # Fila total - texto con color en lugar de fondo
                ('TEXTCOLOR', (0, -1), (-1, -1), orange_color),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                ('ALIGN', (3, -1), (3, -1), 'RIGHT'),

                # Bordes más finos
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(invoice_table)
            story.append(Spacer(1, 10))

        # COMPROBANTE ADJUNTO (si existe)
        if collection.document:
            story.append(Paragraph("COMPROBANTE ADJUNTO", section_style))

            # Crear tabla para el comprobante
            try:
                document_path = collection.document.path
                if os.path.exists(document_path) and collection.document.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # Imagen compacta
                    img = Image(document_path)
                    img.drawHeight = 3.5*inch  # Más pequeña
                    img.drawWidth = 5*inch     # Más pequeña

                    document_data = [
                        [img]
                    ]
                else:
                    document_data = [
                        [f"Archivo: {collection.document.name}"]
                    ]

                document_table = Table(document_data, colWidths=[7*inch])
                document_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, 0), gray_color),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
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
                    Paragraph(f"Documento adjunto: {collection.document.name}", normal_compact))
                story.append(Spacer(1, 10))

        # PIE DE PÁGINA compacto con dirección
        footer_data = [
            [
                "KOSMO FLOWERS - COMPROBANTE DE COBRO",
                f"Generado: {collection.date.strftime('%d/%m/%Y')}"
            ],
            [
                "Tupigachi - Tabacundo",
                ""
            ]
        ]

        footer_table = Table(footer_data, colWidths=[5*inch, 2*inch])
        footer_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), gray_color),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LINEABOVE', (0, 0), (-1, -1), 0.25, green_color),
        ]))
        story.append(footer_table)

        # Construir el PDF
        doc.build(story)

        # Limpiar archivo temporal del logo si existe
        if temp_logo_path and os.path.exists(temp_logo_path):
            try:
                os.remove(temp_logo_path)
            except Exception:
                pass  # Ignorar errores de limpieza

        # Preparar la respuesta
        buffer.seek(0)
        
        # Crear response con headers apropiados para descarga
        response = HttpResponse(
            buffer.getvalue(), content_type='application/pdf')
        
        # Configurar headers para forzar descarga
        filename = f"comprobante_cobro_{collection.payment_number or collection.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(buffer.getvalue())
        response['Cache-Control'] = 'no-cache'
        response['Pragma'] = 'no-cache'

        return response
