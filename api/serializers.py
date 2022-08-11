from rest_framework import serializers

from .models import Product, ShoppingCartItem


class CartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1, max_value=100)

    class Meta:
        model = ShoppingCartItem
        fields = ("product", "quantity")


class ProductSerializer(serializers.ModelSerializer):
    is_on_sale = serializers.BooleanField(read_only=True)
    current_price = serializers.FloatField(read_only=True)
    # Extend the description field
    description = serializers.CharField(min_length=2, max_length=200)
    cart_items = serializers.SerializerMethodField()
    price = serializers.DecimalField(
        min_value=1.00, max_value=100_000,
        max_digits=None, decimal_places=2
    )
    # Override the sale_start and sale_end, these `help_text` will show
    # in the rest_framework dashboard
    sale_start = serializers.DateTimeField(
        input_formats=["%I:%M %p %d %B %Y"], format=None, allow_null=True,
        help_text="Accepted format is '12:01 PM 16 April 2022",
        style={
            "input_type": "text",
            "placeholder": "12:01 AM 28 July 2022"
        }
    )
    sale_end = serializers.DateTimeField(
        input_formats=["%I:%M %p %d %B %Y"], format=None, allow_null=True,
        help_text="Accepted format is '12:01 PM 16 April 2022",
        style={
            "input_type": "text",
            "placeholder": "12:01 AM 28 July 2022"
        }
    )
    photo = serializers.ImageField(default=None)
    warranty = serializers.FileField(write_only=True, default=None)

    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "sale_start", "sale_end",
                  "is_on_sale", "current_price", "cart_items", "photo", "warranty")
        read_only_fields = ("id",)

    def get_cart_items(self, instance):
        items = ShoppingCartItem.objects.filter(product=instance)
        return CartItemSerializer(items, many=True).data

    def update(self, instance, validated_data):
        # validated_data is safe to since it's been validated beforehand
        if validated_data.get("warranty", None):
            instance.description += "\n\nWarranty Information:\n"
            instance.description += b"; ".join(
                validated_data["warranty"].readlines()
            ).decode()
        return instance


class ProductStatSerializer(serializers.Serializer):
    """
        This is an example of a composite field, which serves to present
        data in a certain way.
    """
    stats = serializers.DictField(
        child=serializers.ListField(
            child=serializers.IntegerField(),
        )
    )
