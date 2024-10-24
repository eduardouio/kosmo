from django.urls import path
from .views import (
    PartnerDetailView,
    PartnerListView,
    PartnerCreateView,
    PartnerUpdateView,
    PartnerDeleteView
)


urlpatterns = [
    path('socios/', PartnerListView.as_view(), name='partner_list'),
    path('socios/<int:pk>/', PartnerDetailView.as_view(), name='partner_detail'),
    path('socios/nuevo/', PartnerCreateView.as_view(), name='partner_create'),
    path('socios/actualizar/<int:pk>/', PartnerUpdateView.as_view(), name='partner_update'),
    path('socios/eliminar/<int:pk>/', PartnerDeleteView.as_view(), name='partner_delete'),
]
