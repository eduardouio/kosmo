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
        all_lines = stock_test.split('\n')
        all_lines = [line.strip() for line in all_lines if line.strip()]
        lines_matches = []
        for line in all_lines:
            pattern = r"([A-Z\s]+)\s+(\d+)(\w{2})(\d{2,4})(\d{2,4})?\s+\$?\s*([\d.]+-?[\d.]*)?"
            matchs = re.findall(pattern, line.replace(',', '.'))
            if matchs:
                lines_matches.append([i for i in matchs[0]])
                continue

            pattern = r"([A-Z]+)\s+(\d+)([A-Z]+)(\d+)"
            matches = re.findall(pattern, line.replace(',', '.'))

            if matches:
                matches = [
                    (i[0], i[1], i[2], i[3], '', '0.00') for i in matches
                ]
                lines_matches.append([i for i in matches[0]])
                continue

            if not matches:
                pattern = r"([A-Za-z\s]+)\s+(\d+)([A-Z]+)(\d+)"
                matches = re.findall(pattern, line.replace(',', '.'))
                lines_matches.append([
                    (i[0], i[1], i[2], i[3], '', '0.00') for i in matches
                ])

        for item in lines_matches:
            line_stock = {
                'quantity_box': int(item[1]),
                'box_model': item[2].upper(),
                'tot_stem_flower': 0,
                'box_items': []
            }
            costs = [float(x) for x in item[5].split('-')]
            was_created = False
            product = Product.get_by_variety(item[0].strip())
            length = [
                int(item[3][i:i+2]) for i in range(0, len(item[3]), 2)
            ]

            if len(costs) != len(length):
                raise ValueError(
                    'El numero de costos y de longitudes no coincide'
                )

            if not product:
                was_created = True
                product = Product.objects.create(
                    name='ROSA ESPECIFICAR',
                    variety=item[0].strip().upper()
                )

            for i in range(len(length)):
                line_stock['box_items'].append({
                    'product': product,
                    'tot_stem_flower': 0,
                    'length': length[i],
                    'stem_cost_price': costs[i],
                    'was_created': was_created
                })
            disponiblility.append(line_stock)

        return disponiblility
