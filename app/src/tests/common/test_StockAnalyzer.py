import pytest
import json
from common import StockAnalyzer
from partners.models import Partner


@pytest.mark.django_db
class TestStockAnalyzer():

    def setup_method(self):
        self.parter = Partner.get_by_parcial_name("kosmo")
        if not self.parter:
            raise Exception("Partner not found")
        
        self.mock_stock_text = """Kosmo Flowers Availability- Oct 14th
        1hb Explorer 40/50 x 250 0,40/0,50"""
        self.stock_analyzer = StockAnalyzer()

    def test_get_stock_kosmo(self):
        disponibility = self.stock_analyzer.get_stock(
            self.mock_stock_text, self.parter
        )
        specected_disponibility = [
            {
                'quantity_box': '1',
                'box_model': 'HB',
                'product': 'EXPLORER',
                'length': ['40', '50'],
                'qty_stem_flower': '250',
                'stem_cost_price': ['0.40', '0.50']
            }
        ]
        assert disponibility == specected_disponibility

    def test_get_stock_floraroma(self):
        partner = Partner.get_by_parcial_name("floraroma")
        if not self.parter:
            raise Exception("Partner not found")
        
        mock_stock_text = "AMARETO 1QB4050 $0.25-0.35"
        disponibility = self.stock_analyzer.get_stock(
            mock_stock_text, partner
        )
        specected_disponibility = [
            {
                'product': 'AMARETO',
                'quantity_box': '1',
                'box_model': 'QB',
                'length': ['40', '50'],
                'qty_stem_flower': '0',
                'stem_cost_price': ['0.25', '0.35']
            }
        ]
        assert disponibility == specected_disponibility