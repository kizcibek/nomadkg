
from django.urls import path

from main.views import *

urlpatterns = [
    path('', MainPageView.as_view(), name='home'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category'),
    path('product-detail/<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('add-product/', add_product, name='add-product'),
    path('update-product/<int:pk>/', update_product, name='update-product'),
    path('delete-product/<int:pk>', DeleteProductView.as_view(), name='delete-product'),
]