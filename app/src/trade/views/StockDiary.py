from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class StockDiary(LoginRequiredMixin, TemplateView):
    template_name = 'forms/stock.html'