from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.exceptions import ValidationError
from rest_framework.generics import (ListAPIView, CreateAPIView,
                                     RetrieveUpdateDestroyAPIView, GenericAPIView)
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer, ProductStatSerializer


class ProductsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ("id",)
    search_fields = ("name", "description")
    pagination_class = ProductsPagination

    def get_queryset(self):
        # Get items that are on sale.
        on_sale = self.request.query_params.get("on_sale", None)
        if on_sale is None:
            return super().get_queryset()
        queryset = Product.objects.all()
        if on_sale.lower() == "true":
            from django.utils import timezone
            now = timezone.now()
            return queryset.filter(
                sale_start__lte=now,
                sale_end__gte=now
            )
        return queryset


class ProductCreate(CreateAPIView):
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        # Overriding this method will prevent a user buy an item for 0.00 or free!
        try:
            price = request.data.get("price")
            if price is not None and float(price) <= 0.0:
                raise ValidationError({"price": "Must be above $0.00"})
        except ValueError:
            raise ValidationError({"price": "A valid number is required"})
        return super().create(request, *args, **kwargs)


class ProductRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = "id"
    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            product = response.data
            cache.set(f"product_data_{product['id']}", {
                "name": product.get("name"),
                "description": product.get("description"),
                "price": product.get("price"),
            })
        return response

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get("id")
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            # Clear product from the cache
            cache.delete(f"product_data_{product_id}")
        return response


class ProductStatsView(GenericAPIView):
    lookup_field = "id"
    serializer_class = ProductStatSerializer
    queryset = Product.objects.all()

    def get(self, request, format=None, id=None):
        obj = self.get_object()
        serializer = ProductStatSerializer({
            "stats": {
                "2022-01-01": [5, 10, 15],
                "2022-01-02": [20, 1, 2]
            }
        })
        return Response(serializer.data)
