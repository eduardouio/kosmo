import json
import pytest
from django.urls import reverse
from django.test import Client

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
        response_data = json.loads(response.json()['data'])
        assert response.status_code == 201
        assert response.json()['message'] == 'Pedido Creado Exitosamente'
        assert response_data['order']['status'] == 'PENDIENTE'
        assert response_data['order']['qb_total'] == 8
        assert response_data['order']['hb_total'] == 0
        assert response_data['order']['discount'] == 0
        assert response_data['order']['total_stem_flower'] == 500
        assert len(response_data['order_detail']) == 3

        boxes_items = 0
        for item in response_data['order_detail']:
            boxes_items += len(item['box_items'])

        assert boxes_items == 5

    @pytest.fixture
    def order_data(self):
        return {
            "customer": {
                "id": 25,
                "name": "Cute Lilies Flower Chocolate&Gifts",
                "business_tax_id": "367889048452",
                "address": "Zone - 55,Street - 820,Building - 9 Muither",
                "country": "Qatar",
                "city": "Doha",
                "website": "None",
                "credit_term": 0,
                "consolidate": False,
                "skype": "None",
                "email": "msartin18@gmail.com",
                "phone": "None",
                "is_active": True,
                "contact": {

                },
                "related_partners": [

                ],
                "is_selected": False
            },
            "order_detail": [
                {
                    "stock_detail_id": 8,
                    "quantity": 2,
                    "is_visible": True,
                    "is_selected": False,
                    "is_in_order": False,
                    "box_model": "QB",
                    "tot_stem_flower": 100,
                    "tot_cost_price_box": 0,
                    "id_user_created": 1,
                    "is_active": True,
                    "partner": {
                        "id": 37,
                        "name": "Finca Kosmo Flowers SA",
                        "short_name": "Kosmo Flowers",
                        "business_tax_id": "20315621889",
                        "address": "",
                        "city": "Cayambe",
                        "default_profit_margin": "0.06",
                        "website": "None",
                        "credit_term": 0,
                        "skype": "None",
                        "email": "None",
                        "phone": "None",
                        "is_active": True
                    },
                    "box_items": [
                        {
                            "id": 10,
                            "stock_detail_id": 8,
                            "product_id": 1,
                            "product_name": "ROSA",
                            "product_variety": "AKITO",
                            "product_image": "",
                            "product_colors": [
                                "BLANCO",
                                "CREMA"
                            ],
                            "product_notes": "None",
                            "length": 50,
                            "qty_stem_flower": 100,
                            "stem_cost_price": 0.45,
                            "margin": "0.06",
                            "is_active": True
                        }
                    ],
                    "confirm_delete": False
                },
                {
                    "stock_detail_id": 40,
                    "quantity": 3,
                    "is_visible": True,
                    "is_selected": False,
                    "is_in_order": False,
                    "box_model": "QB",
                    "tot_stem_flower": 200,
                    "tot_cost_price_box": 0.49,
                    "id_user_created": 1,
                    "is_active": True,
                    "partner": {
                        "id": 37,
                        "name": "Finca Kosmo Flowers SA",
                        "short_name": "Kosmo Flowers",
                        "business_tax_id": "20315621889",
                        "address": "",
                        "city": "Cayambe",
                        "default_profit_margin": "0.06",
                        "website": "None",
                        "credit_term": 0,
                        "skype": "None",
                        "email": "None",
                        "phone": "None",
                        "is_active": True
                    },
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
                            "product_notes": "None",
                            "length": 60,
                            "qty_stem_flower": 100,
                            "stem_cost_price": 0.26,
                            "margin": "0.06",
                            "is_active": True
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
                            "product_notes": "None",
                            "length": 50,
                            "qty_stem_flower": 100,
                            "stem_cost_price": 0.23,
                            "margin": "0.06",
                            "is_active": True
                        }
                    ],
                    "confirm_delete": False
                },
                {
                    "stock_detail_id": 40,
                    "quantity": 3,
                    "is_visible": True,
                    "is_selected": False,
                    "is_in_order": False,
                    "box_model": "QB",
                    "tot_stem_flower": 200,
                    "tot_cost_price_box": 0.49,
                    "id_user_created": 1,
                    "is_active": True,
                    "partner": {
                        "id": 37,
                        "name": "Finca Kosmo Flowers SA",
                        "short_name": "Kosmo Flowers",
                        "business_tax_id": "20315621889",
                        "address": "",
                        "city": "Cayambe",
                        "default_profit_margin": "0.06",
                        "website": "None",
                        "credit_term": 0,
                        "skype": "None",
                        "email": "None",
                        "phone": "None",
                        "is_active": True
                    },
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
                            "product_notes": "None",
                            "length": 60,
                            "qty_stem_flower": 100,
                            "stem_cost_price": 0.26,
                            "margin": "0.06",
                            "is_active": True
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
                            "product_notes": "None",
                            "length": 50,
                            "qty_stem_flower": 100,
                            "stem_cost_price": 0.23,
                            "margin": "0.06",
                            "is_active": True
                        }
                    ],
                    "confirm_delete": False
                }
            ]
        }
