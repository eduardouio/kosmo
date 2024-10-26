import re
from products.models import Product
from partners.models import Partner


class StockAnalyzer():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StockAnalyzer, cls).__new__(cls)
        return cls._instance

    def get_stock(self, stock_test, partner):
        if isinstance(partner, int):
            partner = Partner.get_partner_by_id(partner)

        provider = {
            'fincakosmoflowerssa': self.kosmo_provider,
            'fincafloraromasa': self.floraroma_provider
        }
        provider_method = provider.get(partner.name.lower().replace(' ', ''))
        if not provider_method:
            raise ValueError('No provider found for partner {}'.format(
                partner.name)
            )

        return provider_method(stock_test)

    def kosmo_provider(self, stock_test):
        disponiblility = []

        pattern = r"(\d+)(\w{2}) (\D+) (\d+\/?\d*) x (\d+) ([\d.\/]+)"
        matches = re.findall(pattern, stock_test.replace(',', '.'))
        for item in matches:
            line_stock = {
                'quantity_box': int(item[0]),
                'box_model': item[1].upper(),
                'tot_stem_flower': int(item[4]),
                'box_items': []
            }
            stems = [int(x) for x in item[3].split('/')]
            costs = [float(x) for x in item[5].split('/')]
            is_single = len(stems) == 1
            product = Product.get_by_variety(item[2].strip())
            was_created = False

            for i in range(len(stems)):
                if not product:
                    was_created = True
                    product = Product.objects.create(
                        name='ROSA - ESPECIFICAR',
                        variety=item[2].strip()
                    )

                line_stock['box_items'].append({
                    'product': product,
                    'tot_stem_flower': int(item[4]) if is_single else 0,
                    'length': stems[i],
                    'stem_cost_price': costs[i],
                    'was_created': was_created
                })
            disponiblility.append(line_stock)

        return disponiblility

    def floraroma_provider(self, stock_test):
        disponiblility = []
        pattern = r"([A-Z\s]+)\s+(\d+)(\w{2})(\d{2,4})(\d{2,4})?\s+\$?\s*([\d.]+-?[\d.]*)?"
        matches = re.findall(pattern, stock_test.replace(',', '.'))
        for item in matches:
            disponiblility.append({
                'product': item[0].upper(),
                'quantity_box': item[1],
                'box_model': item[2].upper(),
                'length': re.findall(r'\d{2}', item[3]),
                'qty_stem_flower': '0',
                'stem_cost_price': re.findall(r'[\d.]+', item[5]),
            })
        return disponiblility
