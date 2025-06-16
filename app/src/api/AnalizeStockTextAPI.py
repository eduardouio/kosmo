import json
from django.views.generic import View
from django.http import JsonResponse
from partners.models import Partner
from products.models import Product, StockDay, StockDetail, BoxItems
from common import TextPrepare, GPTDirectProcessor
from common.AppLoger import loggin_event


class AnalizeStockTextAPI(View):
    def post(self, request, *args, **kwargs):
        loggin_event('AnalizeStockTextAPI Post request')
        data = json.loads(request.body)
        partner = Partner.get_by_id(data['supplier']['id'])
        stock_day = StockDay.get_by_id(data['idStock'])
        if not stock_day:

            raise Exception('StockDay not found')
        text_stock = TextPrepare().process(data['stockText'])
        loggin_event(f'Texto a procesar: {text_stock}')
        profit_margin = data['profitMargin']
        profit_is_included = data['supplier']['is_profit_margin_included']
        if text_stock is None:
            return JsonResponse(
                {'message': 'Texto no válido'}, safe=False, status=400
            )

        result_dispo = GPTDirectProcessor().process_text(text_stock)
        loggin_event(f'Resultado del procesamiento de texto: {result_dispo}')

        if not result_dispo or not isinstance(result_dispo, list):
            return JsonResponse(
                {
                    'message': 'No se pudieron procesar los datos del stock',
                    'data': str(result_dispo),
                    'status': 'error'
                },
                safe=False,
                status=400
            )

        if len(result_dispo) == 0:
            return JsonResponse(
                {'message': 'No se encontraron datos de stock', 'status': 'error'},
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
            quantity = item[0]  # Cantidad de cajas
            box_model = item[1]  # Modelo de caja
            varieties = item[2]  # Array de variedades
            lengths = item[3]   # Array de largos
            stem_quantities = item[4]  # Array de cantidades de tallos
            prices = item[5]    # Array de precios

            # Determinar tallos por ramo según el tipo de caja
            stems_per_bunch = 12 if box_model == 'EB' else 25

            # Calcular total de tallos para el StockDetail
            total_stems = sum(stem_quantities)

            stock_detail = StockDetail(
                stock_day=kwargs['stock_day'],
                partner=kwargs['partner'],
                quantity=quantity,
                box_model=box_model,
                tot_stem_flower=total_stems,
            )
            stock_detail.save()

            # Crear BoxItems para cada variedad
            for idx in range(len(varieties)):
                product = self.get_or_create_product(varieties[idx])

                # Obtener el precio correspondiente
                price = float(prices[idx]) if idx < len(prices) else 0.00

                if kwargs['profit_is_included']:
                    price = price - \
                        float(kwargs['profit_margin']
                              ) if price > 0.00 else 0.00

                # Calcular cantidad de tallos para esta variedad
                qty_stems = stem_quantities[idx] if idx < len(stem_quantities) else 0
                
                # Calcular total de ramos para esta variedad
                total_bunches = qty_stems // stems_per_bunch if qty_stems > 0 else 0

                BoxItems.objects.create(
                    stock_detail=stock_detail,
                    product=product,
                    stem_cost_price=price,
                    profit_margin=kwargs['profit_margin'],
                    length=lengths[idx] if idx < len(lengths) else 0,
                    qty_stem_flower=qty_stems,
                    total_bunches=total_bunches,
                    stems_bunch=stems_per_bunch,
                )
        return True

    def get_or_create_product(self, variety):
        product = Product.get_by_variety(variety)
        if not product:
            product = Product(
                variety=variety.upper(),
                name='ROSA',
            )
            product.save()
        return product
