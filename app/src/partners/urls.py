from django.urls import path
from .views import (
    PartnerDetailView,
    PartnerListView,
    PartnerCreateView,
    PartnerUpdateView,
    PartnerDeleteView,
    PartnerUpdateParent,
    PartnerAutoRegister,
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
    DAECreateView,
    DAEUpdateView,
    DAEDeleteView,
    DAEListView,
    DAEDetailView,
    PartnerAutoRegisterList,
)

urlpatterns = [
    # URLs específicas deben ir ANTES de las URLs con parámetros variables
    path('socios/nuevo/', PartnerCreateView.as_view(), name='partner_create'),
    path('socios/auto-registro/', PartnerAutoRegister.as_view(), name='partner_auto_register'),
    path('socios/auto-registro/lista/', PartnerAutoRegisterList.as_view(), name='partner_auto_register_list'),
    path('socios/actualizar/<int:pk>/', PartnerUpdateView.as_view(), name='partner_update'),
    path('socios/eliminar/<int:pk>/', PartnerDeleteView.as_view(), name='partner_delete'),
    path('socios/actualizar-parent/<int:pk>/', PartnerUpdateParent.as_view(), name='partner_update_parent'),
    
    # URLs específicas para clientes y proveedores con nombres únicos
    path('socios/clientes/', PartnerListView.as_view(), {'source_page': 'clientes'}, name='customers_list'),
    path('socios/proveedores/', PartnerListView.as_view(), {'source_page': 'proveedores'}, name='supliers_list'),
    
    # URLs con parámetros variables van después
    path('socios/<int:pk>/', PartnerDetailView.as_view(), name='partner_detail'),
    
    # URLs de módulos relacionados
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
    path('dae/', DAEListView.as_view(), name='dae_list'),
    path('dae/<int:pk>/', DAEDetailView.as_view(), name='dae_detail'),
    path('dae/nuevo/<int:id_partner>/', DAECreateView.as_view(), name='dae_create'),
    path('dae/actualizar/<int:pk>/', DAEUpdateView.as_view(), name='dae_update'),
    path('dae/eliminar/<int:pk>/', DAEDeleteView.as_view(), name='dae_delete'),    
]
