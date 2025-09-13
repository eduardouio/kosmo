from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from trade.forms import CreditNoteForm, CreditNoteDetailFormSet
from trade.models.CreditNote import CreditNote
from trade.models.Invoice import Invoice
from trade.models.Payment import Payment, PaymentDetail


class CreditNoteCreateView(View):
    template_name = 'forms/creditnote_form.html'

    def get(self, request, *args, **kwargs):
        invoice_id = request.GET.get('invoice')
        partner_id = request.GET.get('partner')
        initial = {}
        
        if invoice_id:
            invoice = get_object_or_404(Invoice, pk=invoice_id)
            initial['invoice'] = invoice
            initial['partner'] = invoice.partner
        elif partner_id:
            initial['partner'] = partner_id
            
        form = CreditNoteForm(initial=initial)
        
        # Si hay factura inicial, configurar el formulario apropiadamente
        if invoice_id:
            invoice = get_object_or_404(Invoice, pk=invoice_id)
            form.fields['invoice'].queryset = Invoice.objects.filter(
                partner=invoice.partner,
                is_active=True,
                type_document='FAC_VENTA'
            ).exclude(status='ANULADO')
            form.fields['invoice'].widget.attrs.update({'disabled': False})
        elif partner_id:
            # Si solo hay partner, configurar queryset de facturas
            form.fields['invoice'].queryset = Invoice.objects.filter(
                partner_id=partner_id,
                is_active=True,
                type_document='FAC_VENTA'
            ).exclude(status='ANULADO')
            form.fields['invoice'].widget.attrs.update({'disabled': False})
        
        formset = CreditNoteDetailFormSet()
        context = {
            'form': form,
            'formset': formset,
            'title_page': 'Nueva Nota de Crédito',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        print("POST request recibido para CreditNote")
        print("POST data:", request.POST)
        
        form = CreditNoteForm(request.POST)
        formset = CreditNoteDetailFormSet(request.POST)
        
        # Configurar queryset del campo invoice basado en partner seleccionado
        partner_id = request.POST.get('partner')
        if partner_id:
            try:
                form.fields['invoice'].queryset = Invoice.objects.filter(
                    partner_id=partner_id,
                    is_active=True,
                    type_document='FAC_VENTA'
                ).exclude(status='ANULADO')
                form.fields['invoice'].widget.attrs.pop('disabled', None)
            except Exception as e:
                print(f"Error configurando queryset de facturas: {e}")
        
        print("Form válido:", form.is_valid())
        if not form.is_valid():
            print("Errores del form:", form.errors)
            
        print("Formset válido:", formset.is_valid())
        if not formset.is_valid():
            print("Errores del formset:", formset.errors)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                credit_note: CreditNote = form.save(commit=False)
                # Monto total desde detalles si existen
                total_from_details = 0
                for f in formset.forms:
                    if not f.cleaned_data or f.cleaned_data.get('DELETE'):
                        continue
                    qty = f.cleaned_data.get('quantity') or 0
                    unit = f.cleaned_data.get('unit_price') or 0
                    total_from_details += qty * unit
                
                # Ajustar monto si difiere de los detalles
                if (total_from_details and
                        abs(total_from_details - credit_note.amount) > 0.01):
                    credit_note.amount = total_from_details
                    
                credit_note.save()
                formset.instance = credit_note
                formset.save()

                invoice = credit_note.invoice
                
                # Crear cobro asociado a la nota de crédito
                payment = Payment(
                    date=credit_note.date,
                    amount=credit_note.amount,
                    method='NC',
                    type_transaction='INGRESO',
                    status='CONFIRMADO',
                    notes=f'Generado por NC {credit_note.num_credit_note}'
                )
                
                # Generar número de pago si no se proporciona
                if not payment.payment_number:
                    payment.payment_number = (
                        Payment.get_next_collection_number()
                    )
                
                payment.save()
                
                # Crear detalle del cobro
                PaymentDetail.objects.create(
                    payment=payment,
                    invoice=invoice,
                    amount=credit_note.amount
                )
                
                # Actualizar ID del pago en la nota de crédito
                credit_note.id_payment = payment.id
                credit_note.save()
                
                # Actualizar estado de pago de la factura
                invoice.update_payment_status()
            messages.success(request, 'Nota de crédito creada correctamente.')
            return redirect(reverse(
                'creditnote_detail', args=[credit_note.pk]
            ))
        else:
            print("Formulario no válido")
            if not form.is_valid():
                print("Errores del form principal:", form.errors)
            if not formset.is_valid():
                print("Errores del formset:", formset.errors)
            messages.error(
                request, 'Por favor corrige los errores en el formulario.'
            )
            
            # Si hay errores, configurar el queryset para mostrar el formulario
            partner_id = request.POST.get('partner')
            if partner_id:
                try:
                    form.fields['invoice'].queryset = Invoice.objects.filter(
                        partner_id=partner_id,
                        is_active=True,
                        type_document='FAC_VENTA'
                    ).exclude(status='ANULADO')
                    form.fields['invoice'].widget.attrs.pop('disabled', None)
                except Exception as e:
                    print(f"Error configurando queryset en error: {e}")
        
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'title_page': 'Nueva Nota de Crédito'
        })
