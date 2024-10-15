import json
import re
from django.core import serializers
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from partners.models import Partner
from products.models import Product


class StockDiary(LoginRequiredMixin, TemplateView):
    template_name = 'forms/stock-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        partners = Partner.get_suppliers()
        context['title_page'] = 'Disponibilidad'
        context['products_json'] = serializers.serialize('json', products)
        context['partners_json'] = serializers.serialize('json', partners)
        context['products'] = products
        context['partners'] = partners
        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        pattern = r"(\d+)(\w{2}) (\D+) (\d+\/?\d*) x (\d+) ([\d.\/]+)"
        matches = re.findall(pattern, data['stock_text'].replace(',', '.'))
        disponiblility = []
        for item in matches:
            disponiblility.append({
                'quantity_box': item[0],
                'box_model': item[1].upper(),
                'product': item[2].upper(),
                'length': item[3].split('/'),
                'qty_stem_flower': item[4],
                'stem_cost_price': item[5].split('/'),
            })

        return JsonResponse(disponiblility, safe=False)
