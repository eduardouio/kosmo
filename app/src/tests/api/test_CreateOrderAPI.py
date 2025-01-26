import pytest
from django.urls import reverse
from django.test import Client
import json

from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestStockDetailAPI():

    @pytest.fixture
    def client(self):
        client = Client()
        client.force_login(CustomUserModel.get('eduardouio7@gmail.com'))
        return Client()

    @ pytest.fixture
    def url(self):
        return reverse('create_order')

    def test_create_order(self, client, url, order_data):
        response = client.post(
            url,
            order_data,
            content_type='application/json'
        )
        assert response.status_code == 200
        assert response.json()['message'] == 'Pedido creado correctamente'

    @pytest.fixture
    def order_data(self):
        return """{
        "customer": {
            "id": 21,
            "name": "L.A.Premium/Vinbal Inc",
            "business_tax_id": "39052048452",
            "address": "Alhambra/ California",
            "country": "Estados Unidos",
            "city": "Estados Unidos",
            "website": null,
            "credit_term": 30,
            "consolidate": false,
            "skype": null,
            "email": "lorefalco@hotmail.com",
            "phone": null,
            "is_active": true,
            "contact": {},
            "related_partners": [],
            "is_selected": false
        },
        "order": [
            {
                "stock_detail_id": 40,
                "box_items": [
                    {
                        "id": 57,
                        "stock_detail_id": 40,
                        "product_id": 26,
                        "product_name": "ROSA",
                        "product_variety": "SWEET AKITO",
                        "product_image": "/media/products/ROSA-SWEET_AKITO.jpg",
                        "product_colors": [
                            "ROSADO",
                            "BLANCO"
                        ],
                        "product_notes": null,
                        "length": 60,
                        "qty_stem_flower": 200,
                        "stem_cost_price": 0.26,
                        "margin": "0.06",
                        "is_active": true
                    },
                    {
                        "id": 56,
                        "stock_detail_id": 40,
                        "product_id": 2,
                        "product_name": "ROSA",
                        "product_variety": "VENDELA",
                        "product_image": "/media/products/ROSA-VENDELA.jpg",
                        "product_colors": [
                            "CREMA",
                            "AMARILLO"
                        ],
                        "product_notes": null,
                        "length": 50,
                        "qty_stem_flower": 200,
                        "stem_cost_price": 0.23,
                        "margin": "0.06",
                        "is_active": true
                    }
                ],
                "quantity": 3,
                "is_visible": true,
                "is_selected": false,
                "is_in_order": false,
                "box_model": "HB",
                "tot_stem_flower": 400,
                "tot_cost_price_box": 0.49,
                "id_user_created": 1,
                "is_active": true,
                "partner": {
                    "id": 37,
                    "name": "Finca Kosmo Flowers SA",
                    "short_name": "Kosmo Flowers",
                    "business_tax_id": "20315621889",
                    "address": "",
                    "city": "Cayambe",
                    "default_profit_margin": "0.06",
                    "website": null,
                    "credit_term": 0,
                    "skype": null,
                    "email": null,
                    "phone": null,
                    "is_active": true
                },
                "confirm_delete": false
            },
            {
                "stock_detail_id": 39,
                "box_items": [
                    {
                        "id": 54,
                        "stock_detail_id": 39,
                        "product_id": 14,
                        "product_name": "ROSA",
                        "product_variety": "TARA",
                        "product_image": "/media/products/ROSA-TARA.jpg",
                        "product_colors": [
                            "AMARILLO",
                            "CREMA"
                        ],
                        "product_notes": null,
                        "length": 60,
                        "qty_stem_flower": 100,
                        "stem_cost_price": 0.45,
                        "margin": "0.06",
                        "is_active": true
                    }
                ],
                "quantity": 1,
                "is_visible": true,
                "is_selected": false,
                "is_in_order": false,
                "box_model": "QB",
                "tot_stem_flower": 100,
                "tot_cost_price_box": 0,
                "id_user_created": 1,
                "is_active": true,
                "partner": {
                    "id": 37,
                    "name": "Finca Kosmo Flowers SA",
                    "short_name": "Kosmo Flowers",
                    "business_tax_id": "20315621889",
                    "address": "",
                    "city": "Cayambe",
                    "default_profit_margin": "0.06",
                    "website": null,
                    "credit_term": 0,
                    "skype": null,
                    "email": null,
                    "phone": null,
                    "is_active": true
                },
                "confirm_delete": false
            },
            {
                "stock_detail_id": 38,
                "box_items": [
                    {
                        "id": 53,
                        "stock_detail_id": 38,
                        "product_id": 25,
                        "product_name": "ROSA",
                        "product_variety": "SWEET UNIQUE",
                        "product_image": "/media/products/ROSA-SWEET_UNIQUE.jpg",
                        "product_colors": [
                            "ROSADO",
                            "CREMA"
                        ],
                        "product_notes": null,
                        "length": 60,
                        "qty_stem_flower": 152,
                        "stem_cost_price": 0.45,
                        "margin": "0.06",
                        "is_active": true
                    },
                    {
                        "id": 52,
                        "stock_detail_id": 38,
                        "product_id": 25,
                        "product_name": "ROSA",
                        "product_variety": "SWEET UNIQUE",
                        "product_image": "/media/products/ROSA-SWEET_UNIQUE.jpg",
                        "product_colors": [
                            "ROSADO",
                            "CREMA"
                        ],
                        "product_notes": null,
                        "length": 50,
                        "qty_stem_flower": 100,
                        "stem_cost_price": 0.4,
                        "margin": "0.06",
                        "is_active": true
                    }
                ],
                "quantity": 1,
                "is_visible": true,
                "is_selected": false,
                "is_in_order": false,
                "box_model": "QB",
                "tot_stem_flower": 252,
                "tot_cost_price_box": 0.85,
                "id_user_created": 1,
                "is_active": true,
                "partner": {
                    "id": 37,
                    "name": "Finca Kosmo Flowers SA",
                    "short_name": "Kosmo Flowers",
                    "business_tax_id": "20315621889",
                    "address": "",
                    "city": "Cayambe",
                    "default_profit_margin": "0.06",
                    "website": null,
                    "credit_term": 0,
                    "skype": null,
                    "email": null,
                    "phone": null,
                    "is_active": true
                },
                "confirm_delete": false
            },
            {
                "stock_detail_id": 37,
                "box_items": [
                    {
                        "id": 51,
                        "stock_detail_id": 37,
                        "product_id": 25,
                        "product_name": "ROSA",
                        "product_variety": "SWEET UNIQUE",
                        "product_image": "/media/products/ROSA-SWEET_UNIQUE.jpg",
                        "product_colors": [
                            "ROSADO",
                            "CREMA"
                        ],
                        "product_notes": null,
                        "length": 50,
                        "qty_stem_flower": 10,
                        "stem_cost_price": 0.4,
                        "margin": "0.06",
                        "is_active": true
                    },
                    {
                        "id": 50,
                        "stock_detail_id": 37,
                        "product_id": 25,
                        "product_name": "ROSA",
                        "product_variety": "SWEET UNIQUE",
                        "product_image": "/media/products/ROSA-SWEET_UNIQUE.jpg",
                        "product_colors": [
                            "ROSADO",
                            "CREMA"
                        ],
                        "product_notes": null,
                        "length": 40,
                        "qty_stem_flower": 125,
                        "stem_cost_price": 0.3,
                        "margin": "0.06",
                        "is_active": true
                    }
                ],
                "quantity": 1,
                "is_visible": true,
                "is_selected": false,
                "is_in_order": false,
                "box_model": "QB",
                "tot_stem_flower": 135,
                "tot_cost_price_box": 0.7,
                "id_user_created": 1,
                "is_active": true,
                "partner": {
                    "id": 37,
                    "name": "Finca Kosmo Flowers SA",
                    "short_name": "Kosmo Flowers",
                    "business_tax_id": "20315621889",
                    "address": "",
                    "city": "Cayambe",
                    "default_profit_margin": "0.06",
                    "website": null,
                    "credit_term": 0,
                    "skype": null,
                    "email": null,
                    "phone": null,
                    "is_active": true
                },
                "confirm_delete": false
            }
        ]
}
"""
