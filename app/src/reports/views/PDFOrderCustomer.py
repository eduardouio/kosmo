from django.views.generic import TemplateView
from trade.models import Order
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML


# http://localhost:8000/reports/order/1/
class PDFOrderCustomer(TemplateView):
    template_name = 'reports/order_customer.html'

    def get(self, request, id_order, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        order = Order.get_order_by_id(id_order)
        ctx['order'] = order
        html_render = render_to_string(self.template_name, ctx)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "inline; filename=order_customer.pdf"
        response["Content-Encoding"] = "UTF-8"
        HTML(string=html_render).write_pdf(response)
        return response

