from django.urls import path
from .home import HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]