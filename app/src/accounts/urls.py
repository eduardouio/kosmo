from django.urls import path
from .views import LoginTV, LogoutRV

app_name = 'accounts'


urlpatterns = [
    path('accounts/login/', LoginTV.as_view(), name='login'),
    path('accounts/logout/', LogoutRV.as_view(), name='logout'),
]