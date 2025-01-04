import json
from django.views.generic import View
from django.http import JsonResponse
from partners.models import Partner
from products.models import Product, StockDay, StockDetail, BoxItems
from common import GPTProcessor, TextPrepare


class AnalizeStockTextAPI(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        partner = Partner.get_partner_by_id(data['supplier']['id'])
        stock_day = StockDay.get_by_id(data['idStock'])
        if not stock_day:

            raise Exception('StockDay not found')
        text_stock = TextPrepare().process(data['stockText'])
        profit_margin = data['profitMargin']
        profit_is_included = data['supplier']['is_profit_margin_included']
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

        if not data['appendStock']:
            StockDetail.disable_stock_detail(stock_day, partner)

        if (self.create_stock_items(**{
            'result_dispo': result_dispo,
            'stock_day': stock_day,
            'partner': partner,
            'profit_margin': profit_margin,
            'profit_is_included': profit_is_included
        }
        )):
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

    def create_stock_items(self, **kwargs):
        for item in kwargs['result_dispo']:
            stock_detail = StockDetail(
                stock_day=kwargs['stock_day'],
                partner=kwargs['partner'],
                quantity=item[0],
                box_model=item[1],
                tot_stem_flower=item[2],
            )
            stock_detail.save()
            product = self.get_or_create_product(item[4])
            for idx in range(len(item[5])):
                price = float(item[-1][idx])
                if kwargs['profit_is_included']:
                    price = price - float(kwargs['profit_margin']) if price > 0.00 else 0.00

                length = item[-2]
                BoxItems.objects.create(
                    stock_detail=stock_detail,
                    product=product,
                    stem_cost_price=price,
                    profit_margin=kwargs['profit_margin'],
                    length=length[idx],
                    qty_stem_flower=item[2],
                )
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
