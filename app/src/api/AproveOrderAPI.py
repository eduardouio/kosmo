import json
from django.views import View
from django.http import JsonResponse


class AproveOrderAPI(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        import ipdb;ipdb.set_trace()
