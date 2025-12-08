from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import date, datetime, timedelta
import json
import traceback

from partners.models import Partner
from trade.models import Invoice, Payment, PaymentDetail
from common.AppLoger import loggin_event
from common.InvoiceBalance import InvoiceBalance


class PaymentContextData(View):
    """
    API completa para manejar datos de pagos y contexto para aplicaciones Vue.js
    Endpoints disponibles:
    - GET: Obtener datos de contexto general de pagos
    - POST: Crear o actualizar pagos
    """

    def get(self, request):
        """
        Obtiene datos de contexto según la acción solicitada
        """
        action = request.GET.get("action", "context_data")

        if action == "context_data":
            return self._get_payment_context_data(request)
        elif action == "partner_invoices":
            return self._get_partner_invoices(request)
        elif action == "payment_list":
            return self._get_payment_list(request)
        elif action == "payment_detail":
            return self._get_payment_detail(request)
        elif action == "payment_statistics":
            return self._get_payment_statistics(request)
        elif action == "overdue_payments":
            return self._get_overdue_payments(request)
        else:
            return JsonResponse(
                {"success": False, "error": "Acción no válida"}, status=400
            )

    def post(self, request):
        """
        Maneja operaciones POST para pagos
        """
        action = request.POST.get("action", "create_payment")

        if action == "create_payment":
            return self._create_payment(request)
        elif action == "update_payment":
            return self._update_payment(request)
        elif action == "delete_payment":
            return self._delete_payment(request)
        elif action == "apply_payment":
            return self._apply_payment_to_invoices(request)
        else:
            return JsonResponse(
                {"success": False, "error": "Acción POST no válida"}, status=400
            )

    def _get_payment_context_data(self, request):
        """
        Proporciona todos los datos necesarios para el formulario de pagos
        """
        try:

            suppliers = Partner.objects.filter(
                is_active=True, type_partner="PROVEEDOR"
            ).values("id", "name", "business_tax_id")

            loggin_event(
                "DEBUG", f"PaymentContextData: {len(suppliers)} proveedores encontrados"
            )

            # Filtrar facturas de compra que tienen una factura de venta asociada
            # Basado en la relación: ORD_VENTA -> ORD_COMPRA -> FAC_COMPRA
            # Solo mostrar FAC_COMPRA donde existe FAC_VENTA en la cadena
            from trade.models import Order

            # Obtener las órdenes de compra que tienen una orden de venta padre
            purchase_orders_with_sales = Order.objects.filter(
                type_document="ORD_COMPRA",
                parent_order_id__isnull=False,
                parent_order__type_document="ORD_VENTA",
                parent_order__status__in=["CONFIRMADO", "FACTURADO"],
                is_active=True,
            ).values_list("id", flat=True)

            # Filtrar facturas de compra pendientes
            pending_invoices = (
                Invoice.objects.filter(
                    type_document="FAC_COMPRA",
                    status="PENDIENTE",
                    is_active=True,
                    order_id__in=purchase_orders_with_sales,  # Solo facturas con orden de compra relacionada a venta
                )
                .select_related("partner", "order", "order__parent_order")
                .values(
                    "id",
                    "serie",
                    "consecutive",
                    "num_invoice",
                    "partner__id",
                    "partner__name",
                    "date",
                    "due_date",
                    "total_price",
                    "order__id",
                    "order__parent_order__id",
                )
            )

            loggin_event(
                "DEBUG",
                f"PaymentContextData: {len(pending_invoices)} "
                f"facturas pendientes encontradas (con venta asociada)",
            )

            invoices_with_balance = []
            for invoice in pending_invoices:
                try:

                    paid_amount_result = PaymentDetail.objects.filter(
                        invoice_id=invoice["id"],
                        payment__is_active=True,
                        payment__type_transaction="EGRESO",
                    ).aggregate(total=Sum("amount"))

                    paid_amount = paid_amount_result["total"] or Decimal("0.00")

                    total_amount = Decimal(str(invoice["total_price"]))
                    balance = total_amount - paid_amount

                    if balance > Decimal("0.01"):
                        days_overdue = 0

                        if invoice["due_date"]:
                            try:
                                if hasattr(invoice["due_date"], "date"):
                                    due_date = invoice["due_date"].date()
                                else:
                                    due_date = invoice["due_date"]

                                if due_date < date.today():
                                    days_overdue = (date.today() - due_date).days
                                else:
                                    days_overdue = -((due_date - date.today()).days)
                            except Exception as date_error:
                                loggin_event(
                                    "WARNING",
                                    f"PaymentContextData: Error calculando "
                                    f"días vencidos para factura "
                                    f'{invoice["id"]}: {str(date_error)}',
                                )
                                days_overdue = 0

                        formatted_date = ""
                        formatted_due_date = ""

                        try:
                            if invoice["date"]:
                                if hasattr(invoice["date"], "strftime"):
                                    formatted_date = invoice["date"].strftime(
                                        "%Y-%m-%d"
                                    )
                                else:
                                    formatted_date = str(invoice["date"])[:10]
                        except Exception:
                            formatted_date = ""

                        try:
                            if invoice["due_date"]:
                                if hasattr(invoice["due_date"], "strftime"):
                                    formatted_due_date = invoice["due_date"].strftime(
                                        "%Y-%m-%d"
                                    )
                                else:
                                    formatted_due_date = str(invoice["due_date"])[:10]
                        except Exception:
                            formatted_due_date = ""

                        invoices_with_balance.append(
                            {
                                "id": invoice["id"],
                                "serie": invoice["serie"] or "",
                                "consecutive": invoice["consecutive"] or 0,
                                "num_invoice": invoice["num_invoice"] or "",
                                "partner_id": invoice["partner__id"],
                                "partner_name": (
                                    invoice["partner__name"] or "Sin nombre"
                                ),
                                "date": formatted_date,
                                "due_date": formatted_due_date,
                                "total_amount": float(total_amount),
                                "paid_amount": float(paid_amount),
                                "balance": float(balance),
                                "days_overdue": days_overdue,
                            }
                        )

                except Exception as invoice_error:
                    loggin_event(
                        "ERROR",
                        f"PaymentContextData: Error procesando factura "
                        f'{invoice.get("id", "unknown")}: {str(invoice_error)}',
                    )
                    continue

            statistics = self._calculate_payment_statistics(invoices_with_balance)
            payment_config = self._get_payment_configuration()

            response_data = {
                "suppliers": list(suppliers),
                "pending_invoices": invoices_with_balance,
                "payment_methods": payment_config["payment_methods"],
                "popular_banks": payment_config["popular_banks"],
                "statistics": statistics,
                "current_date": date.today().strftime("%Y-%m-%d"),
                "success": True,
            }

            loggin_event(
                "INFO",
                f"PaymentContextData: Datos obtenidos exitosamente "
                f"para usuario {request.user}. "
                f"Facturas: {len(invoices_with_balance)}, "
                f"Proveedores: {len(suppliers)}",
            )
            return JsonResponse(response_data)

        except Exception as e:
            return self._handle_error(e, "obtener datos de contexto de pagos")

    def _get_partner_invoices(self, request):
        """
        Obtiene facturas pendientes de un proveedor específico
        """
        try:
            partner_id = request.GET.get("partner_id")
            if not partner_id:
                return JsonResponse(
                    {"success": False, "error": "ID de proveedor requerido"}, status=400
                )

            pending_invoices = InvoiceBalance.get_pending_invoices(partner_id)

            invoices_data = []
            for invoice_data in pending_invoices:
                invoice = invoice_data["invoice"]
                invoices_data.append(
                    {
                        "id": invoice.id,
                        "serie": invoice.serie,
                        "consecutive": invoice.consecutive,
                        "num_invoice": invoice.num_invoice,
                        "date": invoice.date.strftime("%Y-%m-%d"),
                        "due_date": (
                            invoice.due_date.strftime("%Y-%m-%d")
                            if invoice.due_date
                            else ""
                        ),
                        "total_amount": float(invoice_data["total_amount"]),
                        "paid_amount": float(invoice_data["paid_amount"]),
                        "balance": float(invoice_data["balance"]),
                    }
                )

            return JsonResponse({"success": True, "invoices": invoices_data})

        except Exception as e:
            return self._handle_error(e, "obtener facturas del proveedor")

    def _get_payment_list(self, request):
        """
        Obtiene lista paginada de pagos con filtros
        """
        try:

            page = int(request.GET.get("page", 1))
            per_page = int(request.GET.get("per_page", 20))
            search = request.GET.get("search", "")
            status = request.GET.get("status", "")
            date_from = request.GET.get("date_from", "")
            date_to = request.GET.get("date_to", "")
            partner_id = request.GET.get("partner_id", "")

            payments = (
                Payment.objects.filter(is_active=True, type_transaction="EGRESO")
                .select_related()
                .order_by("-date", "-id")
            )

            if search:
                payments = payments.filter(
                    Q(payment_number__icontains=search)
                    | Q(bank__icontains=search)
                    | Q(nro_operation__icontains=search)
                )

            if status:
                payments = payments.filter(status=status)

            if date_from:
                payments = payments.filter(date__gte=date_from)

            if date_to:
                payments = payments.filter(date__lte=date_to)

            paginator = Paginator(payments, per_page)
            page_obj = paginator.get_page(page)

            payments_data = []
            for payment in page_obj:

                invoice_details = PaymentDetail.objects.filter(
                    payment=payment
                ).select_related("invoice")

                facturas_info = []
                for detail in invoice_details:
                    facturas_info.append(
                        {
                            "id": detail.invoice.id,
                            "num_invoice": detail.invoice.num_invoice,
                            "amount_paid": float(detail.amount),
                        }
                    )

                payments_data.append(
                    {
                        "id": payment.id,
                        "payment_number": payment.payment_number,
                        "date": payment.date.strftime("%Y-%m-%d"),
                        "due_date": (
                            payment.due_date.strftime("%Y-%m-%d")
                            if payment.due_date
                            else ""
                        ),
                        "amount": float(payment.amount),
                        "method": payment.method,
                        "method_display": payment.get_method_display(),
                        "status": payment.status,
                        "bank": payment.bank or "",
                        "nro_operation": payment.nro_operation or "",
                        "facturas": facturas_info,
                        "total_facturas": len(facturas_info),
                    }
                )

            return JsonResponse(
                {
                    "success": True,
                    "payments": payments_data,
                    "pagination": {
                        "current_page": page_obj.number,
                        "total_pages": paginator.num_pages,
                        "total_items": paginator.count,
                        "has_next": page_obj.has_next(),
                        "has_previous": page_obj.has_previous(),
                        "per_page": per_page,
                    },
                }
            )

        except Exception as e:
            return self._handle_error(e, "obtener lista de pagos")

    def _get_payment_detail(self, request):
        """
        Obtiene detalles completos de un pago específico
        """
        try:
            payment_id = request.GET.get("payment_id")
            if not payment_id:
                return JsonResponse(
                    {"success": False, "error": "ID de pago requerido"}, status=400
                )

            payment = Payment.objects.get(id=payment_id, is_active=True)

            invoice_details = PaymentDetail.objects.filter(
                payment=payment
            ).select_related("invoice", "invoice__partner")

            facturas_data = []
            for detail in invoice_details:
                facturas_data.append(
                    {
                        "id": detail.invoice.id,
                        "serie": detail.invoice.serie,
                        "consecutive": detail.invoice.consecutive,
                        "num_invoice": detail.invoice.num_invoice,
                        "partner_name": detail.invoice.partner.name,
                        "total_invoice": float(detail.invoice.total_price),
                        "amount_paid": float(detail.amount),
                        "date": detail.invoice.date.strftime("%Y-%m-%d"),
                    }
                )

            payment_data = {
                "id": payment.id,
                "payment_number": payment.payment_number,
                "date": payment.date.strftime("%Y-%m-%d"),
                "due_date": (
                    payment.due_date.strftime("%Y-%m-%d") if payment.due_date else ""
                ),
                "amount": float(payment.amount),
                "method": payment.method,
                "method_display": payment.get_method_display(),
                "status": payment.status,
                "bank": payment.bank or "",
                "nro_account": payment.nro_account or "",
                "nro_operation": payment.nro_operation or "",
                "document_url": payment.document.url if payment.document else "",
                "created_at": payment.created_at.strftime("%Y-%m-%d %H:%M"),
                "created_by": payment.created_by.username if payment.created_by else "",
                "facturas": facturas_data,
                "total_facturas_amount": sum(f["amount_paid"] for f in facturas_data),
            }

            return JsonResponse({"success": True, "payment": payment_data})

        except Payment.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Pago no encontrado"}, status=404
            )
        except Exception as e:
            return self._handle_error(e, "obtener detalles del pago")

    def _get_payment_statistics(self, request):
        """
        Obtiene estadísticas generales de pagos
        """
        try:
            current_month = datetime.now().month
            current_year = datetime.now().year

            monthly_payments = Payment.objects.filter(
                type_transaction="EGRESO",
                date__month=current_month,
                date__year=current_year,
                is_active=True,
            ).aggregate(total_amount=Sum("amount"), count=Count("id"))

            overdue_payments = Payment.objects.filter(
                type_transaction="EGRESO",
                status="PENDIENTE",
                due_date__lt=date.today(),
                is_active=True,
            ).aggregate(total_amount=Sum("amount"), count=Count("id"))

            pending_invoices = Invoice.objects.filter(
                type_document="FAC_COMPRA", status="PENDIENTE", is_active=True
            ).aggregate(total_amount=Sum("total_price"), count=Count("id"))

            next_month = date.today() + timedelta(days=30)
            upcoming_payments = Payment.objects.filter(
                type_transaction="EGRESO",
                status="PENDIENTE",
                due_date__range=[date.today(), next_month],
                is_active=True,
            ).aggregate(total_amount=Sum("amount"), count=Count("id"))

            statistics = {
                "monthly_payments": {
                    "total_amount": float(monthly_payments.get("total_amount", 0) or 0),
                    "count": monthly_payments.get("count", 0) or 0,
                },
                "overdue_payments": {
                    "total_amount": float(overdue_payments.get("total_amount", 0) or 0),
                    "count": overdue_payments.get("count", 0) or 0,
                },
                "pending_invoices": {
                    "total_amount": float(pending_invoices.get("total_amount", 0) or 0),
                    "count": pending_invoices.get("count", 0) or 0,
                },
                "upcoming_payments": {
                    "total_amount": float(
                        upcoming_payments.get("total_amount", 0) or 0
                    ),
                    "count": upcoming_payments.get("count", 0) or 0,
                },
            }

            return JsonResponse({"success": True, "statistics": statistics})

        except Exception as e:
            return self._handle_error(e, "obtener estadísticas de pagos")

    def _get_overdue_payments(self, request):
        """
        Obtiene pagos vencidos con detalles
        """
        try:
            overdue_payments = Payment.objects.filter(
                type_transaction="EGRESO",
                status="PENDIENTE",
                due_date__lt=date.today(),
                is_active=True,
            ).order_by("due_date")

            payments_data = []
            for payment in overdue_payments:
                days_overdue = (date.today() - payment.due_date).days

                payments_data.append(
                    {
                        "id": payment.id,
                        "payment_number": payment.payment_number,
                        "amount": float(payment.amount),
                        "due_date": payment.due_date.strftime("%Y-%m-%d"),
                        "days_overdue": days_overdue,
                        "method": payment.get_method_display(),
                        "bank": payment.bank or "",
                        "status": payment.status,
                    }
                )

            return JsonResponse(
                {
                    "success": True,
                    "overdue_payments": payments_data,
                    "total_amount": sum(p["amount"] for p in payments_data),
                    "total_count": len(payments_data),
                }
            )

        except Exception as e:
            return self._handle_error(e, "obtener pagos vencidos")

    def _create_payment(self, request):
        """
        Crea un nuevo pago
        """
        try:
            data = json.loads(request.body) if request.body else request.POST

            required_fields = ["date", "amount", "method"]
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse(
                        {"success": False, "error": f"Campo {field} es requerido"},
                        status=400,
                    )

            payment = Payment()
            payment.date = data.get("date")
            payment.amount = Decimal(str(data.get("amount")))
            payment.method = data.get("method")
            payment.bank = data.get("bank", "")
            payment.nro_account = data.get("nro_account", "")
            payment.nro_operation = data.get("nro_operation", "")
            payment.type_transaction = "EGRESO"
            payment.created_by = request.user

            payment.payment_number = Payment.get_next_payment_number()

            payment.save()

            invoice_payments = data.get("invoice_payments", {})
            if invoice_payments:
                self._process_invoice_payments(payment, invoice_payments)

            return JsonResponse(
                {
                    "success": True,
                    "payment_id": payment.id,
                    "payment_number": payment.payment_number,
                    "message": "Pago creado exitosamente",
                }
            )

        except Exception as e:
            return self._handle_error(e, "crear pago")

    def _update_payment(self, request):
        """
        Actualiza un pago existente
        """
        try:
            data = json.loads(request.body) if request.body else request.POST
            payment_id = data.get("payment_id")

            if not payment_id:
                return JsonResponse(
                    {"success": False, "error": "ID de pago requerido"}, status=400
                )

            payment = Payment.objects.get(id=payment_id, is_active=True)

            if data.get("date"):
                payment.date = data.get("date")
            if data.get("amount"):
                payment.amount = Decimal(str(data.get("amount")))
            if data.get("method"):
                payment.method = data.get("method")
            if "bank" in data:
                payment.bank = data.get("bank", "")
            if "nro_account" in data:
                payment.nro_account = data.get("nro_account", "")
            if "nro_operation" in data:
                payment.nro_operation = data.get("nro_operation", "")

            payment.updated_by = request.user
            payment.save()

            if "invoice_payments" in data:

                PaymentDetail.objects.filter(payment=payment).delete()

                self._process_invoice_payments(payment, data["invoice_payments"])

            return JsonResponse(
                {"success": True, "message": "Pago actualizado exitosamente"}
            )

        except Payment.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Pago no encontrado"}, status=404
            )
        except Exception as e:
            return self._handle_error(e, "actualizar pago")

    def _delete_payment(self, request):
        """
        Elimina (desactiva) un pago
        """
        try:
            data = json.loads(request.body) if request.body else request.POST
            payment_id = data.get("payment_id")

            if not payment_id:
                return JsonResponse(
                    {"success": False, "error": "ID de pago requerido"}, status=400
                )

            payment = Payment.objects.get(id=payment_id, is_active=True)
            payment.is_active = False
            payment.updated_by = request.user
            payment.save()

            return JsonResponse(
                {"success": True, "message": "Pago eliminado exitosamente"}
            )

        except Payment.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Pago no encontrado"}, status=404
            )
        except Exception as e:
            return self._handle_error(e, "eliminar pago")

    def _apply_payment_to_invoices(self, request):
        """
        Aplica un pago a facturas específicas
        """
        try:
            data = json.loads(request.body) if request.body else request.POST
            payment_id = data.get("payment_id")
            invoice_payments = data.get("invoice_payments", {})

            if not payment_id or not invoice_payments:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "ID de pago e información de facturas requeridos",
                    },
                    status=400,
                )

            payment = Payment.objects.get(id=payment_id, is_active=True)

            InvoiceBalance.apply_payment_to_invoices(payment_id, invoice_payments)

            return JsonResponse(
                {"success": True, "message": "Pago aplicado a facturas exitosamente"}
            )

        except Payment.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Pago no encontrado"}, status=404
            )
        except Exception as e:
            return self._handle_error(e, "aplicar pago a facturas")

    def _process_invoice_payments(self, payment, invoice_payments):
        """
        Procesa las asociaciones de pago con facturas
        """
        for invoice_id, amount in invoice_payments.items():
            try:
                invoice = Invoice.objects.get(id=invoice_id, is_active=True)

                PaymentDetail.objects.create(
                    payment=payment, invoice=invoice, amount=Decimal(str(amount))
                )

            except Invoice.DoesNotExist:
                loggin_event(
                    "WARNING",
                    f"Factura {invoice_id} no encontrada al procesar pago {payment.id}",
                )
                continue
            except Exception as e:
                loggin_event(
                    "ERROR",
                    f"Error procesando factura {invoice_id} para pago {payment.id}: {str(e)}",
                )
                continue

    def _calculate_payment_statistics(self, invoices_with_balance):
        """
        Calcula estadísticas de pagos
        """
        try:
            current_month = datetime.now().month
            current_year = datetime.now().year

            overdue_payments = Payment.objects.filter(
                type_transaction="EGRESO",
                status="PENDIENTE",
                due_date__lt=date.today(),
                is_active=True,
            ).aggregate(total_amount=Sum("amount"), count=Count("id"))

            monthly_payments = Payment.objects.filter(
                type_transaction="EGRESO",
                date__month=current_month,
                date__year=current_year,
                is_active=True,
            ).aggregate(total_amount=Sum("amount"), count=Count("id"))

            total_pending_invoices = len(invoices_with_balance)
            total_pending_amount = sum(inv["balance"] for inv in invoices_with_balance)

            next_month_date = date.today() + timedelta(days=30)
            upcoming_invoices = [
                inv
                for inv in invoices_with_balance
                if (
                    inv["due_date"]
                    and datetime.strptime(inv["due_date"], "%Y-%m-%d").date()
                    <= next_month_date
                )
            ]

            return {
                "overdue_payments": {
                    "total_amount": float(overdue_payments.get("total_amount", 0) or 0),
                    "count": overdue_payments.get("count", 0) or 0,
                },
                "monthly_payments": {
                    "total_amount": float(monthly_payments.get("total_amount", 0) or 0),
                    "count": monthly_payments.get("count", 0) or 0,
                },
                "pending_invoices": {
                    "total_amount": float(total_pending_amount),
                    "count": total_pending_invoices,
                },
                "upcoming_due_invoices": {
                    "count": len(upcoming_invoices),
                    "total_amount": float(
                        sum(inv["balance"] for inv in upcoming_invoices)
                    ),
                },
            }

        except Exception as e:
            loggin_event(
                "ERROR", f"PaymentContextData: Error calculando estadísticas: {str(e)}"
            )
            return {
                "overdue_payments": {"total_amount": 0, "count": 0},
                "monthly_payments": {"total_amount": 0, "count": 0},
                "pending_invoices": {"total_amount": 0, "count": 0},
                "upcoming_due_invoices": {"count": 0, "total_amount": 0},
            }

    def _get_payment_methods(self):
        """Obtiene los métodos de pago disponibles"""
        try:

            methods = [
                {"value": "TRANSF", "label": "Transferencia Bancaria"},
                {"value": "EFECTIVO", "label": "Efectivo"},
                {"value": "CHEQUE", "label": "Cheque"},
                {"value": "TC", "label": "Tarjeta de Crédito"},
                {"value": "TD", "label": "Tarjeta de Débito"},
                {"value": "NC", "label": "Nota de Crédito"},
                {"value": "OTRO", "label": "Otro"},
            ]

            return methods

        except Exception as e:
            loggin_event(
                "ERROR", f"PaymentContextData: Error obteniendo métodos: {str(e)}"
            )
            return []

    def _get_payment_configuration(self):
        """
        Obtiene configuración de métodos de pago y bancos
        """
        try:

            payment_methods = self._get_payment_methods()

            today = date.today()
            if today.month > 6:
                six_months_ago = today.replace(month=today.month - 6)
            else:
                six_months_ago = today.replace(
                    month=today.month + 6, year=today.year - 1
                )

            popular_banks = (
                Payment.objects.filter(
                    type_transaction="EGRESO",
                    date__gte=six_months_ago,
                    bank__isnull=False,
                    is_active=True,
                )
                .values("bank")
                .annotate(count=Count("id"))
                .order_by("-count")[:10]
            )

            return {
                "payment_methods": payment_methods,
                "popular_banks": list(popular_banks),
            }

        except Exception as e:
            loggin_event(
                "ERROR", f"PaymentContextData: Error obteniendo configuración: {str(e)}"
            )
            return {"payment_methods": [], "popular_banks": []}

    def _handle_error(self, error, operation):
        """
        Maneja errores de manera consistente
        """
        error_msg = str(error)
        loggin_event("ERROR", f"PaymentContextData: Error en {operation} - {error_msg}")

        traceback_info = traceback.format_exc()
        loggin_event(
            "ERROR", f"PaymentContextData: Traceback completo - {traceback_info}"
        )

        return JsonResponse(
            {
                "error": f"Error al {operation}: {error_msg}",
                "success": False,
                "debug_info": (
                    traceback_info
                    if hasattr(self, "request") and self.request.user.is_superuser
                    else None
                ),
            },
            status=500,
        )
