from django.views.generic import TemplateView


class PDFTest(TemplateView):
    template_name = 'reports/order_customer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'PDF Test'
        return context