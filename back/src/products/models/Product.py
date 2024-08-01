from django.db import models
from common import BaseModel


class Product(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    common_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    variety = models.CharField(max_length=255)
    stem_length = models.CharField(max_length=50)
    bud_thickness = models.CharField(max_length=50)
    color = models.CharField(max_length=100)
    box_type = models.CharField(max_length=50)
    box_capacity = models.IntegerField()
    box_dimensions = models.CharField(max_length=100)
    box_weight = models.DecimalField(max_digits=5, decimal_places=2)
    origin_farm = models.CharField(max_length=255)
    daily_availability = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    box_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_fluctuations = models.TextField(blank=True, null=True)
    export_code = models.CharField(max_length=50)
    destination_region = models.CharField(max_length=255)
    transportation_cost = models.DecimalField(max_digits=10, decimal_places=2)
    transportation_provider = models.CharField(max_length=255)
    available_credits = models.CharField(max_length=100)
    payment_terms = models.CharField(max_length=100)
    additional_notes = models.TextField(blank=True, null=True)
    customer_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.common_name