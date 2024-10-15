import json
import re
from django.core import serializers
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from partners.models import Partner
from products.models import Product
from  common import StockAnalyzer


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
        stock_analyzer = StockAnalyzer()
        disponiblility = stock_analyzer.get_stock(
            data['stock_text'], data['id_partner']
        )
        return JsonResponse({}, status=200)
