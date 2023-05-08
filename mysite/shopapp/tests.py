from string import ascii_letters
from random import choices

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # cls.user = User.objects.create_superuser(username="bob_test", password='qwerty')
        cls.user = User.objects.create_user(username="bob_test", password='qwerty')
        cls.user.user_permissions.add(Permission.objects.get(codename='add_product'))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "A good table",
                "discount": "10",
            }
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name='Best product')

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'users-fixture.json',
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        # for product in Product.objects.filter(archived=False).all():
        #     self.assertContains(response, product.name)
        # products = Product.objects.filter(archived=False).all()
        # products_ = response.contents["products"]
        # for p, p_ in zip(products, products_):
        #     self.assertEqual(p.pk, p_.pk)
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'users-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(
            reverse("shopapp:products-export"),
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )


class OrderListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # cls.credentials = dict(username="bob_test", password='qwerty')
        # cls.user = User.objects.create_user(**cls.credentials)
        cls.user = User.objects.create_user(username="bob_test", password='qwerty')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        # self.client.login(**self.credentials)
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        # self.assertRedirects(response, str(settings.LOGIN_URL))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="Max", password='qwerty')
        cls.user.user_permissions.add(Permission.objects.get(codename='view_order'))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()
        # cls.order.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address='ul. Pyshkina, d 13',
            promocode='123code',
            user_id=self.user.id,
        )

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
        )
        response_order = response.context['order']
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Order.objects.filter(delivery_address=self.order.delivery_address).exists()
        )
        self.assertTrue(
            Order.objects.filter(promocode=self.order.promocode).exists()
        )
        self.assertEqual(response_order.pk, self.order.pk)


