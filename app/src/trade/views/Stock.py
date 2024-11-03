import json
from django.core.serializers import serialize
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from partners.models import Partner
from products.models import Product
from common import StockAnalyzer


class Stock(LoginRequiredMixin, TemplateView):
    template_name = 'forms/stock-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        partners = Partner.get_suppliers()
        context['title_page'] = 'Disponibilidad'
        context['products_json'] = serialize('json', products)
        context['partners_json'] = serialize('json', partners)
        context['products'] = products
        context['partners'] = partners
        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        stock_analyzer = StockAnalyzer()
        print('llamado')
        disponiblility = stock_analyzer.get_stock(
            data['stock_text'], data['id_partner']
        )
        print('disponiblility')
        disponiblility = self.serialize_dipo(disponiblility)
        print('response')
        return JsonResponse({"data": json.dumps(disponiblility)}, status=200)

    def serialize_dipo(self, disponibility):
        for itm in disponibility:
            for p in itm['box_items']:
                product = json.loads(serialize('json', [p['product']]))[0]
                p['product'] = {
                    'id': product['pk'], **product['fields']
                }


        return disponibility
