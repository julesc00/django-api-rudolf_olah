from django.urls import path

from .views import ProductList, ProductCreate, ProductRetrieveUpdateDestroy, ProductStatsView

app_name = "api"

urlpatterns = [
    path("v1/products/", ProductList.as_view(), name="list-products"),
    path("v1/products/new", ProductCreate.as_view(), name="create-product"),
    path("v1/products/<int:id>/", ProductRetrieveUpdateDestroy.as_view(), name="update-delete-product"),
    path("v1/products/<int:id>/stats", ProductStatsView.as_view(), name="stats"),
]
