import pytest
from common import StockAnalyzer
from partners.models import Partner
from products.models import Product


@pytest.mark.django_db
class TestsockAnalyzerFloraroma():

    def setup_method(self):
        self.stock_analyzer = StockAnalyzer()
        self.partner = Partner.get_by_parcial_name('floraroma')

    def test_floraroma_sigle(self):
        if not self.partner:
            raise Exception("Partner not found")

        mock_stock_text = """
        HOT EXPLORER 1QB40 $0.40
        """
        product = Product.get_by_variety('HOT EXPLORER')
        disponibility = self.stock_analyzer.get_stock(
            mock_stock_text, self.partner
        )
        spected_data = [{
            'quantity_box': 1,
            'box_model': 'QB',
            'tot_stem_flower': 0,
            'box_items': [{
                'product': product,
                'tot_stem_flower': 0,
                'length': 40,
                'stem_cost_price': 0.4,
                'was_created': False
            }]
        }]
        assert disponibility == spected_data

    def test_floraroma_multiple(self):
        if not self.partner:
            raise Exception("Partner not found")

        mock_stock_text = """
        AMARETO 10QB4050 $0.25-0.35
        """
        product = Product.get_by_variety('AMARETO')
        disponibility = self.stock_analyzer.get_stock(
            mock_stock_text, self.partner
        )
        spected_data = [{
            'quantity_box': 10,
            'box_model': 'QB',
            'tot_stem_flower': 0,
            'box_items': [{
                'product': product,
                'tot_stem_flower': 0,
                'length': 40,
                'stem_cost_price': 0.25,
                'was_created': False
            }, {
                'product': product,
                'tot_stem_flower': 0,
                'length': 50,
                'stem_cost_price': 0.35,
                'was_created': False
            }]
        }]
        assert disponibility == spected_data

    def test_single_case_1(self):
        if not self.partner:
            raise Exception("Partner not found")

        mock_stock_text = """
        MOMENTUM 1QB40
        """
        product = Product.get_by_variety('MOMENTUM')
        disponibility = self.stock_analyzer.get_stock(
            mock_stock_text, self.partner
        )
        spected_data = [{
            'quantity_box': 1,
            'box_model': 'QB',
            'tot_stem_flower': 0,
            'box_items': [{
                'product': product,
                'tot_stem_flower': 0,
                'length': 40,
                'stem_cost_price': 0.00,
                'was_created': False
            }]
        }]
        assert disponibility == spected_data

        def test_single_case_1(self):
            if not self.partner:
                raise Exception("Partner not found")

            mock_stock_text = """
            DEEP PURPLE 1QB40
            """
            product = Product.get_by_variety('DEEP PURPLE')
            disponibility = self.stock_analyzer.get_stock(
                mock_stock_text, self.partner
            )
            spected_data = [{
                'quantity_box': 1,
                'box_model': 'QB',
                'tot_stem_flower': 0,
                'box_items': [{
                    'product': product,
                    'tot_stem_flower': 0,
                    'length': 40,
                    'stem_cost_price': 0.00,
                    'was_created': False
                }]
            }]
            assert disponibility == spected_data

    def test_all_words_two_words(self):
        mock_stock_text = """
        AMOROSA 4QB5060 $0.35-0.40
        SOUL 12HB40  $0.30
        SWEET MEMORY 10QB40
        """
        product_amorosa = Product.get_by_variety('AMOROSA')
        product_soul = Product.get_by_variety('SOUL')
        product_sweet_memory = Product.get_by_variety('SWEET MEMORY')

        disponibility = self.stock_analyzer.get_stock(
            mock_stock_text, self.partner
        )

        spected_data = [{
            'quantity_box': 4,
            'box_model': 'QB',
            'tot_stem_flower': 0,
            'box_items': [{
                'product': product_amorosa,
                'tot_stem_flower': 0,
                'length': 50,
                'stem_cost_price': 0.35,
                'was_created': False
            },
                {
                'product': product_amorosa,
                'tot_stem_flower': 0,
                'length': 60,
                'stem_cost_price': 0.40,
                'was_created': False
            }]
        }, {
            'quantity_box': 12,
            'box_model': 'HB',
            'tot_stem_flower': 0,
            'box_items': [{
                'product': product_soul,
                'tot_stem_flower': 0,
                'length': 40,
                'stem_cost_price': 0.30,
                'was_created': False
            }]
        }, {
            'quantity_box': 10,
            'box_model': 'QB',
            'tot_stem_flower': 0,
            'box_items': [{
                'product': product_sweet_memory,
                'tot_stem_flower': 0,
                'length': 40,
                'stem_cost_price': 0.00,
                'was_created': False
            }]
        }]

        assert disponibility == spected_data

        def test_floraroma_dont_exist(self):
            if not self.partner:
                raise Exception("Partner not found")

            mock_stock_text = """
            HOT MEGA 1QB40 $0.40
            """
            disponibility = self.stock_analyzer.get_stock(
                mock_stock_text, self.partner
            )
            product = Product.get_by_variety('HOT MEGA')
            spected_data = [{
                'quantity_box': 1,
                'box_model': 'QB',
                'tot_stem_flower': 0,
                'box_items': [{
                    'product': product,
                    'tot_stem_flower': 0,
                    'length': 40,
                    'stem_cost_price': 0.4,
                    'was_created': False
                }]
            }]
            assert disponibility == spected_data
