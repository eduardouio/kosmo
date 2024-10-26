import pytest
import json
from common import StockAnalyzer
from partners.models import Partner
from products.models import Product


@pytest.mark.django_db
class TestStockAnalyzer():

    def setup_method(self):
        self.stock_analyzer = StockAnalyzer()

    def test_get_stock_kosm_single(self):
        stock_entry = """
        1qb Freedom 40 x 125 0,30
        """

        partner = Partner.get_by_parcial_name("kosmo")
        product = Product.get_by_variety("Freedom")

        spected_data = [{
            'quantity_box': 1,
            'box_model': 'QB',
            'tot_stem_flower': 125,
            'box_items': [{
                'product': product,
                'tot_stem_flower': 0,
                'length': 40,
                'stem_cost_price': 0.30
            }
            ]
        }]

        disponibility = self.stock_analyzer.get_stock(
            stock_entry, partner
        )

        assert (spected_data == disponibility)

    def test_get_stock_kosm_multiple(self):
        stock_entry = """
        1hb Explorer 40/50 x 250 0,40/0,50
        """

        partner = Partner.get_by_parcial_name("kosmo")
        product = Product.get_by_variety("Explorer")

        spected_data = [{
            'quantity_box': 1,
            'box_model': 'HB',
            'tot_stem_flower': 250,
            'box_items': [{
                'product': product,
                'tot_stem_flower': 0,
                'length': 40,
                'stem_cost_price': 0.40
            }, {
                'product': product,
                'tot_stem_flower': 0,
                'length': 50,
                'stem_cost_price': 0.50
            }]
        }]

        disponibility = self.stock_analyzer.get_stock(
            stock_entry, partner
        )

        assert (spected_data == disponibility)