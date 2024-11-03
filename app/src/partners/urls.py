from django.urls import path
from .views import (
    PartnerDetailView,
    PartnerListView,
    PartnerCreateView,
    PartnerUpdateView,
    PartnerDeleteView,
    PartnerUpdateParent,
    BankCreateView,
    BankUpdateView,
    BankDeleteView,
    BankDetailView,
    BankListView,
    ContactDetailView,
    ContactListView,
    ContactCreateView,
    ContactUpdateView,
    ContactDeleteView,
)

urlpatterns = [
    path('socios/', PartnerListView.as_view(), name='partner_list'),
    path('socios/<int:pk>/', PartnerDetailView.as_view(), name='partner_detail'),
    path('socios/nuevo/', PartnerCreateView.as_view(), name='partner_create'),
    path('socios/actualizar/<int:pk>/', PartnerUpdateView.as_view(), name='partner_update'),
    path('socios/eliminar/<int:pk>/', PartnerDeleteView.as_view(), name='partner_delete'),
    path('socios/actualizar-parent/<int:pk>/', PartnerUpdateParent.as_view(), name='partner_update_parent'),
    path('bancos/', BankListView.as_view(), name='bank_list'),
    path('bancos/<int:pk>/', BankDetailView.as_view(), name='bank_detail'),
    path('bancos/nuevo/<int:id_partner>/', BankCreateView.as_view(), name='bank_create'),
    path('bancos/actualizar/<int:pk>/', BankUpdateView.as_view(), name='bank_update'),
    path('bancos/eliminar/<int:pk>/', BankDeleteView.as_view(), name='bank_delete'),
    path('contactos/', ContactListView.as_view(), name='contact_list'),
    path('contactos/<int:pk>/', ContactDetailView.as_view(), name='contact_detail'),
    path('contactos/nuevo/<int:id_partner>/', ContactCreateView.as_view(), name='contact_create'),
    path('contactos/actualizar/<int:pk>/', ContactUpdateView.as_view(), name='contact_update'),
    path('contactos/eliminar/<int:pk>/', ContactDeleteView.as_view(), name='contact_delete'),
    
]
