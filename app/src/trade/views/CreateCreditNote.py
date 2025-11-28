from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from trade.forms import CreditNoteForm, CreditNoteDetailFormSet
from trade.models.CreditNote import CreditNote
from trade.models.Invoice import Invoice


class CreditNoteCreateView(View):
    template_name = "forms/creditnote_form.html"

    def get_invoice_queryset(self, partner_id=None):
        """Obtiene facturas válidas para nota de crédito"""
        qs = Invoice.objects.filter(
            is_active=True
        ).exclude(status="ANULADO")
        
        if partner_id:
            qs = qs.filter(partner_id=partner_id)
        
        return qs.order_by('-date')

    def calculate_pending_balance(self, invoice):
        """Calcula el saldo pendiente de una factura"""
        total_price = float(invoice.total_price or 0)
        
        # Calcular total pagado
        total_paid = 0
        if hasattr(invoice, 'total_paid'):
            total_paid = float(invoice.total_paid or 0)
        elif hasattr(invoice, 'get_total_paid'):
            total_paid = float(invoice.get_total_paid() or 0)
        
        # Calcular notas de crédito aplicadas a esta factura
        credit_notes_applied = CreditNote.objects.filter(
            invoice=invoice,
            is_active=True,
            status="APLICADO"
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Saldo pendiente = Total - Pagado - Notas de crédito
        return total_price - total_paid - float(credit_notes_applied)

    def get(self, request, *args, **kwargs):
        invoice_id = request.GET.get("invoice")
        partner_id = request.GET.get("partner")
        initial = {}

        form = CreditNoteForm(initial=initial)
        
        if invoice_id:
            invoice = get_object_or_404(Invoice, pk=invoice_id)
            initial["invoice"] = invoice
            initial["partner"] = invoice.partner
            form = CreditNoteForm(initial=initial)
            form.fields["invoice"].queryset = self.get_invoice_queryset(invoice.partner_id)
        elif partner_id:
            initial["partner"] = partner_id
            form = CreditNoteForm(initial=initial)
            form.fields["invoice"].queryset = self.get_invoice_queryset(partner_id)

        formset = CreditNoteDetailFormSet()
        context = {
            "form": form,
            "formset": formset,
            "title_page": "Nueva Nota de Crédito",
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = CreditNoteForm(request.POST)
        formset = CreditNoteDetailFormSet(request.POST)

        partner_id = request.POST.get("partner")
        if partner_id:
            form.fields["invoice"].queryset = self.get_invoice_queryset(partner_id)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                credit_note: CreditNote = form.save(commit=False)

                # Calcular total desde los detalles
                total_from_details = 0
                for f in formset.forms:
                    if not f.cleaned_data or f.cleaned_data.get("DELETE"):
                        continue
                    qty = f.cleaned_data.get("quantity") or 0
                    unit = f.cleaned_data.get("unit_price") or 0
                    total_from_details += qty * unit

                # Actualizar monto si hay detalles
                if total_from_details > 0:
                    credit_note.amount = total_from_details

                # Validar que el monto no exceda el saldo pendiente
                invoice = credit_note.invoice
                if invoice:
                    pending = self.calculate_pending_balance(invoice)
                    if credit_note.amount > pending:
                        messages.error(
                            request, 
                            f"El monto (${credit_note.amount:.2f}) excede el saldo pendiente de la factura (${pending:.2f})"
                        )
                        return render(
                            request,
                            self.template_name,
                            {"form": form, "formset": formset, "title_page": "Nueva Nota de Crédito"},
                        )

                credit_note.status = "APLICADO"
                credit_note.save()
                
                formset.instance = credit_note
                formset.save()

                # Actualizar estado de pago de la factura
                if invoice:
                    invoice.update_payment_status()

            messages.success(request, "Nota de crédito creada correctamente.")
            return redirect(reverse("creditnote_detail", args=[credit_note.pk]))
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")

        return render(
            request,
            self.template_name,
            {"form": form, "formset": formset, "title_page": "Nueva Nota de Crédito"},
        )
