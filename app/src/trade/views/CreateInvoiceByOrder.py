from django.views import View
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from api.CreateInvoiceAPI import CreateInvoiceAPI
from trade.models import Order

class CreateInvoiceByOrder(View):
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        # Simular request para CreateInvoiceAPI
        api_view = CreateInvoiceAPI()
        class DummyRequest:
            def __init__(self, user, body):
                self.user = user
                self.body = body
        import json
        dummy_request = DummyRequest(
            request.user,
            json.dumps({'order_id': order_id})
        )
        response = api_view.post(dummy_request)
        if response.status_code == 201:
            messages.success(request, "Factura generada correctamente.")
        else:
            try:
                error = response.json().get('error', 'Error al generar la factura')
            except Exception:
                error = 'Error al generar la factura'
            messages.error(request, error)
        return redirect(reverse('order_detail_presentation', args=[order_id]))
