import pytest
from common import StockAnalyzer
from partners.models import Partner
from products.models import Product


@pytest.mark.django_db
class TestStockAnalyzerKosmo():

    def setup_method(self):
        self.stock_analyzer = StockAnalyzer()
        self.partner = Partner.get_by_parcial_name("kosmo")

    def test_get_stock_kosm_single(self):
        stock_entry = """
        1qb Freedom 40 x 125 0,30
        """

        product = Product.get_by_variety("Freedom")

        spected_data = [{
            'quantity_box': 1,
            'box_model': 'QB',
            'tot_stem_flower': 125,
            'box_items': [{
                'product': product,
                'tot_stem_flower': 125,
                'length': 40,
                'stem_cost_price': 0.30,
                'was_created': False
            }
            ]
        }]

        disponibility = self.stock_analyzer.get_stock(
            stock_entry, self.partner
        )

        assert (spected_data == disponibility)

    def test_get_stock_kosm_multiple(self):
        stock_entry = """
        1hb Explorer 40/50 x 250 0,40/0,50
        """

        product = Product.get_by_variety("Explorer")

        spected_data = [{
            'quantity_box': 1,
            'box_model': 'HB',
            'tot_stem_flower': 250,
            'box_items': [{
                'product': product,
                'tot_stem_flower': 0,
                'length': 40,
                'stem_cost_price': 0.40,
                'was_created': False
            }, {
                'product': product,
                'tot_stem_flower': 0,
                'length': 50,
                'stem_cost_price': 0.50,
                'was_created': False
            }]
        }]

        disponibility = self.stock_analyzer.get_stock(
            stock_entry, self.partner
        )

        assert (spected_data == disponibility)

    def test_get_stock_kosmo_multiple(self):
        stock_entry = """
        1qb Nena 50/60 x 100 0,40/0,45
        1qb Orange Crush 40 x 125 0,35
        3qb Sweet Unique 50 x 125 0,45
        """
        product_1 = Product.get_by_variety("Nena")
        product_2 = Product.get_by_variety("Orange Crush")
        product_3 = Product.get_by_variety("Sweet Unique")

        spected_data = [{
            'quantity_box': 1,
            'box_model': 'QB',
            'tot_stem_flower': 100,
            'box_items': [{
                'product': product_1,
                'tot_stem_flower': 0,
                'length': 50,
                'stem_cost_price': 0.40,
                'was_created': False
            }, {
                'product': product_1,
                'tot_stem_flower': 0,
                'length': 60,
                'stem_cost_price': 0.45,
                'was_created': False
            }
            ]
        }, {
            'quantity_box': 1,
            'box_model': 'QB',
            'tot_stem_flower': 125,
            'box_items': [{
                'product': product_2,
                'tot_stem_flower': 125,
                'length': 40,
                'stem_cost_price': 0.35,
                'was_created': False
            }
            ]
        }, {
            'quantity_box': 3,
            'box_model': 'QB',
            'tot_stem_flower': 125,
            'box_items': [{
                'product': product_3,
                'tot_stem_flower': 125,
                'length': 50,
                'stem_cost_price': 0.45,
                'was_created': False
            }
            ]
        }]

        disponibility = self.stock_analyzer.get_stock(
            stock_entry, self.partner
        )

        for i in range(len(spected_data)):
            assert (spected_data[i] == disponibility[i])

    def test_get_stock_kosmo_product_not_exist(self):
        stock_entry = """
        1qb Nena Don Found 50/60 x 100 0,40/0,45
        """
        assert Product.get_by_variety("Nena Don Found") is None
        disponibility = self.stock_analyzer.get_stock(
            stock_entry, self.partner
        )
        product = Product.get_by_variety("Nena Don Found")
        spected_data = [{
            'quantity_box': 1,
            'box_model': 'QB',
            'tot_stem_flower': 100,
            'box_items': [{
                'product': product,
                'tot_stem_flower': 0,
                'length': 50,
                'stem_cost_price': 0.40,
                'was_created': True
            }, {
                'product': product,
                'tot_stem_flower': 0,
                'length': 60,
                'stem_cost_price': 0.45,
                'was_created': True
            }]
        }]

        assert (spected_data == disponibility)
