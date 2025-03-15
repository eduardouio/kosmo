import json
from django.views import View
from django.http import JsonResponse


class CancelOrderAPI(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        import ipdb;ipdb.set_trace()
