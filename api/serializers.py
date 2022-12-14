from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "sale_start", "sale_end")
        read_only_fields = ("id",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["is_on_sale"] = instance.is_on_sale()
        data["current_price"] = instance.current_price()
        return data
