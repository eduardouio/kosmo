from django.views.generic import View
from django.http import JsonResponse

from partners.models import Partner
from trade.models import Invoice, Payment, PaymentDetail
from common.AppLoger import loggin_event


class PaymentContextData(View):