import json
from django.core.serializers import serialize
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView, RedirectView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django import forms

from products.models import Stock, Product, StockDay, StockDetail, BoxItems
from partners.models import Partner
from common import GPTProcessor


class StockDetailForm(forms.ModelForm):
    class Meta:
        model = StockDetail
        fields = [
            'partner', 'box_model', 'tot_stem_flower', 'stem_cost_price_box'
        ]
        widgets = {
            'partner': forms.Select(
                attrs={'class': 'form-control form-control-sm',
                       'required': 'required', 'readonly': 'readonly'}
            ),
            'box_model': forms.Select(
                attrs={'class': 'form-control form-control-sm',
                       'required': 'required'}
            ),
            'tot_stem_flower': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm',
                       'placeholder': 'Cantidad de tallos', 'readonly': 'readonly'}
            ),
            'stem_cost_price_box': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm',
                       'placeholder': 'Precio de costo por tallo'}
            ),
        }


class DetailStockCreate(LoginRequiredMixin, TemplateView):
    template_name = 'forms/stock_detail_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_day = StockDay.get_by_id(kwargs['pk'])
        partners = Partner.get_suppliers()
        context['title_section'] = 'Carga Detalle de Stock  {}'.format(
            stock_day.date.strftime('%d/%m/%Y')
        )
        partners_exist_stock = StockDetail.get_partner_by_stock_day(
            stock_day
        )
        context['partners_exist_stock'] = serialize(
            'json', partners_exist_stock
        )
        context['title_page'] = 'Detalle de Stock'
        context['partners'] = partners
        context['partners_json'] = serialize('json', partners)
        context['stock_day'] = stock_day
        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        partner = Partner.get_partner_by_id(data['id_partner'])
        json_dispo = GPTProcessor().process_text(data['stock_text'])

        if isinstance(json_dispo, dict):
            json_dispo = [json_dispo]

        if isinstance(json_dispo[0], dict) and isinstance(json_dispo, list):
            json_dispo = json_dispo[0]['flowers']

        stock_day = StockDay.get_by_id(kwargs['pk'])
        if data['replace']:
            StockDetail.disable_stock_detail(stock_day, partner)

        self.create_stock_items(json_dispo, stock_day, partner)

        return JsonResponse(json_dispo, safe=False, status=201)

    def create_stock_items(self, json_dispo, stock_day, partner):
        import ipdb; ipdb.set_trace()
        for item in json_dispo:
            stock_detail = StockDetail(
                stock_day=stock_day,
                partner=partner,
                box_model=item['box_model'],
                tot_stem_flower=item['tot_stem_flower'],
            )
            stock_detail.save()
            for itm in item['box_items']:
                product = Product.get_by_variety(itm['variety'])
                box_item = BoxItems(
                    stock_detail=stock_detail,
                    product=product,
                    length=itm['length'],
                    qty_stem_flower=itm['tot_stem_flower'],
                    stem_cost_price=itm['stem_cost_price']
                )
                box_item.save()
    
    def get_or_create_product(self, variety):
        product = Product.get_by_variety(variety)
        if not product:
            product = Product(
                variety=variety.upper(),
                name='ROSA VERIFICAR',   
            )
            product.save()
        return product


class DetailStockDetail(LoginRequiredMixin, TemplateView):
    template_name = 'presentations/stock_detail_presentation.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_day = StockDay.get_by_id(kwargs['pk'])
        stock_details = StockDetail.get_by_stock_day(stock_day)
        context['stock_day'] = stock_day
        stock_boxes = []

        for itm in stock_details:
            stock_box = BoxItems.get_box_items(itm)
            stock_boxes.append({
                'stock_detail': itm,
                'boxes': stock_box,
                'total_boxes': len(stock_box)
            })

        context['stock_details'] = stock_boxes
        context['title_page'] = 'Dipobibilidad {}'.format(
            stock_day.date.strftime('%d/%m/%Y')
        )
        context['title_section'] = 'Detalle de Stock {}'.format(
            stock_day.date.strftime('%d/%m/%Y')
        )
        return context


class SingleStockDetailCreateView(LoginRequiredMixin, CreateView):
    model = StockDetail
    form_class = StockDetailForm
    template_name = 'forms/stockdetail_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_bar'] = 'Crear StockDetail'
        return context

    def get_success_url(self):
        return reverse_lazy('stockdetail_detail', kwargs={'pk': self.object.pk}) + '?action=created'


class SingleStockDetailUpdateView(LoginRequiredMixin, UpdateView):
    model = StockDetail
    form_class = StockDetailForm
    template_name = 'forms/stock_item_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Actualizar {}'.format(
            self.object.id
        )
        context['title_section'] = 'Actualizar Item #{} del {}'.format(
            self.object.id, self.object.stock_day.date.strftime('%d/%m/%Y')
        )
        context['stock_day'] = self.object.stock_day
        context['box_items'] = BoxItems.get_box_items(self.object)

        return context

    def get_success_url(self):
        url = reverse_lazy('stock_detail_detail',
                           kwargs={'pk': self.object.pk})
        url = '{url}?action=updated'.format(url=url)
        return url
