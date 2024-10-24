from django.urls import path
from .views import (
    ProductCreateView,
    ProductUpdateView,
    ProductListView,
    ProductDetailView,
    ProductDeleteView,
)

urlpatterns = [
    # product
    path('catalogo/nuevo/', ProductCreateView.as_view(), name='product_create'),
    path('catalogo/lista/', ProductListView.as_view(), name='product_list'),
    path('catalogo/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('catalogo/<int:pk>/actualizar/', ProductUpdateView.as_view(), name='product_update'),
    path('catalogo/<int:pk>/eliminar/', ProductDeleteView.as_view(), name='product_delete'),
]