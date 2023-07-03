"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""

from timeit import default_timer
from csv import DictWriter

from django.contrib.auth.models import Group
from django.contrib.syndication.views import Feed
from django.http import(
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse
)
from django.shortcuts import render, redirect, reverse
from django.core.cache import cache
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin
)
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .common import save_csv_products
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .forms import GroupForm
from .forms import ProductForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer
import logging

logger = logging.getLogger(__name__)


@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.

    Полный CRUD для сущностей товара
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print("hello products list")
        return super().list(*args, **kwargs)

    @extend_schema(
        summary="Get one product by ID",
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment: filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        methods=["post"],
        detail=False,
        parser_classes=[MultiPartParser]
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        # return Response({"ok": True})
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class LatestProductsFeed(Feed):
    title = "Products (latest)"
    description = "Updates on changes and additions products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return Product.objects.filter(archived=False)[:5]

    def item_name(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:100]


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = "delivery_address",
    filterset_fields = [
        "user",
        "delivery_address",
    ]
    ordering_fields = [
        "pk",
        "user",
        "delivery_address",
    ]


class ShopIndexView(View):

    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
            ('Electric stove', 570),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 1,
        }
        logger.debug("Products for shop index: %s", products)
        logger.info("Rendering shop index")
        print("shop index context", context)
        return render(request, "shopapp/shop-index.html", context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)

    def dispatch(self, request, *args, **kwargs):
        logger.info('Запрошена страница со списком товаров')
        response = super().dispatch(request, *args, **kwargs)
        return response


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")

    def test_func(self):
    # return self.request.user.groups.filter(name="secret-group").exists()
        return self.request.user.is_superuser or \
               self.request.user.has_perm(self.permission_required)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        logger.info(f'Пользователь {self.request.user.username} создал новый товар')
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):

    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    form_class = ProductForm
    template_name_suffix = "_update_form"
    permission_required = "shopapp.change_product"

    def test_func(self):
        return self.request.user.is_superuser or \
            self.get_object().created_by == self.request.user and \
            self.request.user.has_perm(self.permission_required)

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})


class OrderListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )

    def dispatch(self, request, *args, **kwargs):
        logger.info('Запрошена страница со списком заказов')
        response = super().dispatch(request, *args, **kwargs)
        return response


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderCreateView(CreateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    success_url = reverse_lazy("shopapp:orders_list")

    def form_valid(self, form):
        logger.info(f'Пользователь {self.request.user.username} создал новый заказ')
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class OrderExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "order_id": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "products": [product.pk for product in order.products.all()]
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})
