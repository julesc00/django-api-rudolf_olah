from django.urls import path

from .views import ProductList, ProductCreate, ProductDelete

app_name = "api"

urlpatterns = [
    path("v1/products/", ProductList.as_view(), name="list-products"),
    path("v1/products/new", ProductCreate.as_view(), name="create-product"),
    path("v1/products/<int:id>/delete", ProductDelete.as_view(), name="delete-product"),
]
