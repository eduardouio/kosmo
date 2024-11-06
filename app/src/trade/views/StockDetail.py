import json
from django.core.serializers import serialize
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Stock, Product, StockDay, StockDetail, BoxItems
from partners.models import Partner
from common import StockAnalyzer


class DetailStockCreate(LoginRequiredMixin, TemplateView):
    template_name = 'forms/stock_detail_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_day = StockDay.get_by_id(kwargs['pk'])
        partners = Partner.get_suppliers()
        context['title_section'] = 'Carga Detalle de Stock  {}'.format(
            stock_day.date.strftime('%d/%m/%Y')
        )
        context['title_page'] = 'Detalle de Stock'
        context['partners'] = partners
        context['partners_json'] = serialize('json', partners)
        context['stock_day'] = stock_day
        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        partner = Partner.get_partner_by_id(data['id_partner'])
        dispo = StockAnalyzer().get_stock(data['stock_text'], partner)
        stock_day = StockDay.get_by_id(kwargs['pk'])
        self.create_stock_items(dispo, stock_day, partner)
        json_dispo = []
        for itm in dispo:
            itm_dispo = {
                'quantity_box': itm['quantity_box'],
                'text_entry': itm['text_entry'],
                'box_model': itm['box_model'],
                'tot_stem_flower': itm['tot_stem_flower'],
                'lines_recived': len(data['stock_text'].split('\n')),
                'lines_analized': len(dispo),
                'box_items': []
            }
            for i in itm['box_items']:
                itm_dispo['box_items'].append({
                    'product': i['product'].id,
                    'name': i['product'].name,
                    'variety': i['product'].variety,
                    'tot_stem_flower': i['tot_stem_flower'],
                    'length': i['length'],
                    'stem_cost_price': i['stem_cost_price'],
                    'was_created': i['was_created'],
                })
            json_dispo.append(itm_dispo)

        return JsonResponse(json_dispo, safe=False, status=201)

    def create_stock_items(self, dispotext, stock_day, partner):
        for item in dispotext:
            stock_detail = StockDetail(
                stock_day=stock_day,
                partner=partner,
                box_model=item['box_model'],
                tot_stem_flower=item['tot_stem_flower'],
            )
            stock_detail.save()
            for itm in item['box_items']:
                product = itm['product']
                box_item = BoxItems(
                    stock_detail=stock_detail,
                    product=product,
                    length=itm['length'],
                    qty_stem_flower=itm['tot_stem_flower'],
                    stem_cost_price=itm['stem_cost_price']
                )
                box_item.save()


class DetailStockDetail(LoginRequiredMixin, TemplateView):
    template_name = 'presentations/stock_detail_presentation.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_day = StockDay.get_by_id(kwargs['pk'])
        context['stock_day'] = stock_day
        context['title_page'] = 'Dipobibilidad {}'.format(
            stock_day.date.strftime('%d/%m/%Y')
        )
        context['title_section'] = 'Detalle de Stock {}'.format(
            stock_day.date.strftime('%d/%m/%Y')
        )
        return context
