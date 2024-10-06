from django.urls import path
from .views import LoginTV, LogoutRV, HomeTV

app_name = 'accounts'


urlpatterns = [
    path('', HomeTV.as_view(), name='home'),
    path('accounts/login/', LoginTV.as_view(), name='login'),
    path('accounts/logout/', LogoutRV.as_view(), name='logout'),
]