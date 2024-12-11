import json
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from partners.models import Partner
from products.models import Stock, Product, StockDay, StockDetail, BoxItems
from common import GPTProcessor, TextPrepare


class DetailStockCreate(LoginRequiredMixin, TemplateView):
    template_name = 'forms/stock_detail_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_day = StockDay.get_by_id(kwargs['pk'])
        partners = Partner.get_suppliers()
        context['title_section'] = 'Carga Detalle de Stock  {}'.format(
            stock_day.date.strftime('%d/%m/%Y')
        )
        partners_exist_stock = StockDetail.get_partner_by_stock_day(
            stock_day
        )
        context['partners_exist_stock'] = serialize(
            'json', partners_exist_stock
        )
        context['title_page'] = 'Detalle de Stock'
        context['partners'] = partners
        context['partners_json'] = serialize('json', partners)
        context['stock_day'] = stock_day
        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        partner = Partner.get_partner_by_id(data['id_partner'])
        stock_day = StockDay.get_by_id(kwargs['pk'])
        text_stock = TextPrepare().process(data['stock_text'])
        if text_stock is None:
            return JsonResponse(
                {'message': 'Texto no válido'}, safe=False, status=400
            )

        result_dispo = GPTProcessor().process_text(text_stock)

        if isinstance(result_dispo, str):
            return JsonResponse(
                {'message': result_dispo, 'status': 'error'},
                safe=False,
                status=400
            )

        if data['replace']:
            StockDetail.disable_stock_detail(stock_day, partner)

        if (self.create_stock_items(result_dispo, stock_day, partner)):
            return JsonResponse(
                {'message': 'ok', 'status': 'success'},
                safe=False,
                status=201
            )

        return JsonResponse(
            {'message': 'Error al cargar el stock', 'status': 'error'},
            safe=False,
            status=400
        )

    def create_stock_items(self, result_dispo, stock_day, partner):
        for item in result_dispo:
            stock_detail = StockDetail(
                stock_day=stock_day,
                partner=partner,
                quantity=item[0],
                box_model=item[1],
                tot_stem_flower=item[2],
                stem_cost_price_box=item[3],
            )
            
            stock_detail.save()
            product = self.get_or_create_product(item[4])
            box_item = BoxItems(
                stock_detail=stock_detail,
                product=product,
                length=item[-1][0],
                qty_stem_flower=item[2],
                stem_cost_price=item[-2][0],
                stem_cost_price_box=item[3],
            )
            box_item.save()
        return True

    def get_or_create_product(self, variety):
        product = Product.get_by_variety(variety)
        if not product:
            product = Product(
                variety=variety.upper(),
                name='ROSA VERIFICAR',
            )
            product.save()
        return product
