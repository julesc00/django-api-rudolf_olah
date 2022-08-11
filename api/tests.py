import os.path

from django.conf import settings

from rest_framework.test import APITestCase

from .models import Product


class ProductCreateTestCase(APITestCase):
    def test_create_product(self):
        initial_product_count = Product.objects.count()
        product_attrs = {
            "name": "New Product",
            "description": "Test product here!",
            "price": "123.45"
        }
        response = self.client.post("api/v1/products/new", product_attrs)
        if response.status_code != 201:
            print(response.data)

        self.assertEqual(
            Product.objects.count(),
            initial_product_count + 1
        )
        for attr, expected_value in product_attrs.items():
            self.assertEqual(response.data[attr], expected_value)
        self.assertEqual(response.data["is_on_sale"], False)
        self.assertEqual(
            response.data["current_price"],
            float(product_attrs["price"])
        )


class ProductDestroyTestCase(APITestCase):
    def test_delete_product(self):
        initial_product_count = Product.objects.count()
        product_id = Product.objects.first().id
        self.client.delete(f"/api/v1/products/{product_id}")
        self.assertEqual(
            Product.objects.count(),
            initial_product_count - 1
        )
        self.assertRaises(
            Product.DoesNotExist,
            Product.objects.get, id=product_id
        )


class ProductListTestCase(APITestCase):
    def test_list_products(self):
        product_count = Product.objects.count()
        response = self.client.get("api/v1/products/")
        self.assertIsNone(response.data.get("next"))
        self.assertIsNone(response.data.get("previous"))
        self.assertEqual(response.data["count"], product_count)
        self.assertEqual(len(response.data["result"]), product_count)


class ProductUpdateTestCase(APITestCase):
    def test_update_product(self):
        product = Product.objects.first()
        response = self.client.patch(
            f"/api/v1/products/{product.id}/",
            {
                "name": "New Product",
                "description": "Awesome product",
                "price": 123.45
            },
            format="json"
        )
        updated = Product.objects.filter(id=product.id).first()
        self.assertEqual(updated.name, "New Product")

    def test_upload_product_photo(self):
        product = Product.objects.first()
        original_photo = product.photo
        photo_path = os.path.join(
            settings.MEDIA_ROOT, "products", "vitamin-iron.jpg"
        )
        with open(photo_path, "rb") as photo_data:
            response = self.client.patch(
                f"api/v1/products/{product.id}",
                {"photo": photo_data},
                format="multipart"
            )

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data.get("photo"), original_photo)

        updated = Product.objects.filter(id=product.id).first()
        try:
            expected_photo = os.path.join(
                settings.MEDIA_ROOT, "products", "vitamin-iron.jpg",
            )
            self.assertTrue(updated.photo.path.startswith(expected_photo))
        finally:
            os.remove(updated.photo.path)
