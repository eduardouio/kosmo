from trade.models import (
    Order,
    OrderBoxItems,
    OrderItems,
    Invoice,
    InvoiceItems,
    InvoiceBoxItems
)
from partners.models import Partner, DAE, Contact
from django.views import View
from django.http import JsonResponse


class CompleteInvoiceInfo(View)
    
    def get(self, id_invoice, *args, **kwargs):
        return JsonResponse(
            {
                'invoice': 'vmax',
                'items': 'vmax',
                'boxes': 'vmax',
            }
        )