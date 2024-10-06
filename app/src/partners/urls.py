from django.urls import path
from .views import PartnerDetailView

app_name = 'partners'


urlpatterns = [
    path('partners/<int:pk>/', PartnerDetailView.as_view(), name='partner-detail'),
]