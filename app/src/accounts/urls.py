from django.urls import path, re_path
from .views import LoginTV, LogoutRV, HomeTV, UserProfileView
from .views.CertValidationView import pki_validation_view

urlpatterns = [
    path('', HomeTV.as_view(), name='home'),
    path('accounts/login/', LoginTV.as_view(), name='login'),
    path('accounts/logout/', LogoutRV.as_view(), name='logout'),
    path('accounts/profile/', UserProfileView.as_view(), name='user_profile'),
    re_path(r'^\.well-known/pki-validation/(?P<filename>.*)$',pki_validation_view,name='pki_validation'),
]
