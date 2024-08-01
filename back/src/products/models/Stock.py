from django.db import models
from common import BaseModel

class Stock(BaseModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    update_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Inventario de {self.product.common_name}"