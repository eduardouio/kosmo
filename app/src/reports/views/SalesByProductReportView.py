from django.views.generic import TemplateView

class SalesByProductReportView(TemplateView):
    template_name = 'reports/sales_by_product_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aquí puedes agregar la lógica para obtener los datos necesarios para el informe
        return context