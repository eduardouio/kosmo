from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Sum
from decimal import Decimal
from datetime import date

from partners.models import Partner
from trade.models import Invoice, Payment, PaymentDetail
from common.AppLoger import loggin_event


class CollectionsContextAPI(View):
    """
    API completa para manejar datos de cobros y contexto para aplicaciones Vue.js
    Endpoints disponibles:
    - GET: Obtener datos de contexto general de cobros
    - POST: Crear o actualizar cobros
    """

    def get(self, request):
        """
        Obtiene datos de contexto según la acción solicitada
        """
        action = request.GET.get("action", "context_data")

        if action == "context_data":
            return self._get_collections_context_data(request)
        elif action == "customer_invoices":
            return self._get_customer_invoices(request)
        elif action == "collection_list":
            return self._get_collection_list(request)
        elif action == "collection_detail":
            return self._get_collection_detail(request)
        elif action == "collection_statistics":
            return self._get_collection_statistics(request)
        elif action == "overdue_collections":
            return self._get_overdue_collections(request)
        else:
            return JsonResponse(
                {"success": False, "error": "Acción no válida"}, status=400
            )

    def post(self, request):
        """
        Maneja operaciones POST para cobros
        """
        action = request.POST.get("action", "create_collection")

        if action == "create_collection":
            return self._create_collection(request)
        elif action == "update_collection":
            return self._update_collection(request)
        elif action == "delete_collection":
            return self._delete_collection(request)
        elif action == "apply_collection":
            return self._apply_collection_to_invoices(request)
        else:
            return JsonResponse(
                {"success": False, "error": "Acción POST no válida"}, status=400
            )

    def _get_collections_context_data(self, request):
        """
        Proporciona todos los datos necesarios para el formulario de cobros
        """
        try:
            loggin_event(
                "INFO", "CollectionsContextAPI: Iniciando carga de datos de contexto"
            )

            customers = self._get_customers()
            pending_invoices = self._get_pending_invoices()
            payment_methods = self._get_payment_methods()
            popular_banks = self._get_popular_banks()
            statistics = self._calculate_statistics(pending_invoices)

            response_data = {
                "success": True,
                "customers": customers,
                "invoices": pending_invoices,
                "payment_methods": payment_methods,
                "popular_banks": popular_banks,
                "statistics": statistics,
                "current_date": date.today().strftime("%Y-%m-%d"),
            }

            loggin_event(
                "INFO",
                f"CollectionsContextAPI: Enviando {len(pending_invoices)} "
                f"facturas pendientes de cobro",
            )

            return JsonResponse(response_data)

        except Exception as e:
            loggin_event("ERROR", f"CollectionsContextAPI error: {str(e)}")

            response_data = {
                "success": False,
                "error": "Error al obtener los datos de contexto de cobros",
            }

            return JsonResponse(response_data, status=500)

    def _get_customers(self):
        """Obtiene la lista de clientes activos"""
        try:
            customers_queryset = Partner.objects.filter(
                is_active=True, type_partner="CLIENTE"
            ).order_by("name")

            customers = []
            for customer in customers_queryset:
                pending_count = Invoice.objects.filter(
                    partner=customer,
                    type_document="FAC_VENTA",
                    status="PENDIENTE",
                    is_active=True,
                ).count()

                customers.append(
                    {
                        "id": customer.id,
                        "name": customer.name,
                        "business_tax_id": (
                            customer.business_tax_id
                            if hasattr(customer, "business_tax_id")
                            else ""
                        ),
                        "pending_invoices": pending_count,
                    }
                )

            loggin_event(
                "INFO", f"CollectionsContextAPI: {len(customers)} clientes cargados"
            )

            return customers

        except Exception as e:
            loggin_event(
                "ERROR", f"CollectionsContextAPI _get_customers error: {str(e)}"
            )
            return []

    def _get_pending_invoices(self):
        """Obtiene facturas de venta con saldo pendiente"""
        try:

            invoices_queryset = (
                Invoice.objects.filter(
                    type_document="FAC_VENTA", is_active=True, status="PENDIENTE"
                )
                .select_related("partner")
                .order_by("-date")
            )

            loggin_event(
                "INFO",
                f"CollectionsContextAPI: {invoices_queryset.count()} "
                f"facturas de venta encontradas",
            )

            pending_invoices = []

            for invoice in invoices_queryset:
                try:

                    balance = self._calculate_invoice_balance(invoice)

                    if balance > 0:

                        if invoice.due_date:
                            days_overdue = (date.today() - invoice.due_date.date()).days
                        else:
                            days_overdue = 0

                        pending_invoices.append(
                            {
                                "id": invoice.id,
                                "order_id": invoice.order.id,
                                "number": (
                                    invoice.num_invoice or f"Factura {invoice.id}"
                                ),
                                "type": invoice.type_document,
                                "customer_id": (
                                    invoice.partner.id if invoice.partner else None
                                ),
                                "customer_name": (
                                    invoice.partner.name
                                    if invoice.partner
                                    else "Sin cliente"
                                ),
                                "customer_document": (
                                    invoice.partner.business_tax_id
                                    if invoice.partner
                                    and hasattr(invoice.partner, "business_tax_id")
                                    else ""
                                ),
                                "date": (
                                    invoice.date.strftime("%Y-%m-%d")
                                    if invoice.date
                                    else ""
                                ),
                                "due_date": (
                                    invoice.due_date.strftime("%Y-%m-%d")
                                    if invoice.due_date
                                    else ""
                                ),
                                "days_overdue": days_overdue,
                                "total_amount": float(invoice.total_invoice),
                                "paid_amount": float(self._get_paid_amount(invoice)),
                                "pending_amount": float(balance),
                                "balance": float(balance),
                            }
                        )

                except Exception as e:
                    loggin_event(
                        "ERROR", f"Error procesando factura {invoice.id}: {str(e)}"
                    )
                    continue

            def sort_key(invoice_data):
                days_overdue = invoice_data["days_overdue"]

                return -days_overdue

            pending_invoices.sort(key=sort_key)

            loggin_event(
                "INFO",
                f"CollectionsContextAPI: {len(pending_invoices)} "
                f"facturas con saldo pendiente (ordenadas por vencimiento)",
            )

            return pending_invoices

        except Exception as e:
            loggin_event(
                "ERROR", f"CollectionsContextAPI _get_pending_invoices error: {str(e)}"
            )
            return []

    def _calculate_invoice_balance(self, invoice):
        """Calcula el saldo pendiente de una factura"""
        try:
            total_amount = invoice.total_invoice
            paid_amount = self._get_paid_amount(invoice)
            return total_amount - paid_amount
        except Exception:
            return Decimal("0.0")

    def _get_paid_amount(self, invoice):
        """Obtiene el monto total pagado de una factura"""
        try:
            paid_total = PaymentDetail.objects.filter(
                invoice=invoice, payment__is_active=True, payment__status="CONFIRMADO"
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.0")

            return paid_total
        except Exception:
            return Decimal("0.0")

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
                "ERROR", f"CollectionsContextAPI _get_payment_methods error: {str(e)}"
            )
            return []

    def _calculate_statistics(self, pending_invoices):
        """Calcula estadísticas de cobros"""
        try:
            if not pending_invoices:
                return {
                    "pending_invoices": {"count": 0, "total_amount": 0},
                    "overdue_collections": {"count": 0, "total_amount": 0},
                    "upcoming_due_invoices": {"count": 0, "total_amount": 0},
                }

            total_pending_amount = sum(inv["balance"] for inv in pending_invoices)

            overdue_invoices = [
                inv for inv in pending_invoices if inv["days_overdue"] > 0
            ]
            overdue_amount = sum(inv["balance"] for inv in overdue_invoices)

            upcoming_due = [
                inv for inv in pending_invoices if -30 <= inv["days_overdue"] <= 0
            ]
            due_soon_amount = sum(inv["balance"] for inv in upcoming_due)

            statistics = {
                "pending_invoices": {
                    "count": len(pending_invoices),
                    "total_amount": float(total_pending_amount),
                },
                "overdue_collections": {
                    "count": len(overdue_invoices),
                    "total_amount": float(overdue_amount),
                },
                "upcoming_due_invoices": {
                    "count": len(upcoming_due),
                    "total_amount": float(due_soon_amount),
                },
            }

            loggin_event(
                "INFO",
                f"CollectionsContextAPI estadísticas: "
                f'{statistics["pending_invoices"]["count"]} facturas, '
                f'${statistics["pending_invoices"]["total_amount"]:.2f} '
                f"pendiente",
            )

            return statistics

        except Exception as e:
            loggin_event(
                "ERROR", f"CollectionsContextAPI _calculate_statistics error: {str(e)}"
            )
            return {
                "pending_invoices": {"count": 0, "total_amount": 0},
                "overdue_collections": {"count": 0, "total_amount": 0},
                "upcoming_due_invoices": {"count": 0, "total_amount": 0},
            }

    def _get_popular_banks(self):
        """Obtiene los bancos más utilizados en cobros recientes"""
        try:
            from django.db.models import Count
            from datetime import date, timedelta

            today = date.today()
            six_months_ago = today - timedelta(days=180)

            popular_banks = (
                Payment.objects.filter(
                    type_transaction="INGRESO",
                    date__gte=six_months_ago,
                    bank__isnull=False,
                    is_active=True,
                    status="CONFIRMADO",
                )
                .values("bank")
                .annotate(count=Count("id"))
                .order_by("-count")[:10]
            )

            return list(popular_banks)

        except Exception as e:
            loggin_event(
                "ERROR", f"CollectionsContextAPI _get_popular_banks error: {str(e)}"
            )
            return []
