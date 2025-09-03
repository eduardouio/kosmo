from django.urls import path, re_path
from .views import LoginTV, LogoutRV, HomeTV, UserProfileView
from .views.SellersListView import SellersListView
from .views.SellerDetailView import SellerDetailView
from .views.SellerCreateView import SellerCreateView
from .views.CertValidationView import pki_validation_view

urlpatterns = [
    path('', HomeTV.as_view(), name='home'),
    path('accounts/login/', LoginTV.as_view(), name='login'),
    path('accounts/logout/', LogoutRV.as_view(), name='logout'),
    path('accounts/profile/', UserProfileView.as_view(), name='user_profile'),
    path(
        'accounts/sellers/',
        SellersListView.as_view(),
        name='sellers_list'
    ),
    path(
        'accounts/sellers/new/',
        SellerCreateView.as_view(),
        name='seller_create'
    ),
    path(
        'accounts/sellers/<int:pk>/',
        SellerDetailView.as_view(),
        name='seller_detail'
    ),
    re_path(
       r'^\.well-known/pki-validation/(?P<filename>.*)$',
       pki_validation_view,
       name='pki_validation'
    ),
]
