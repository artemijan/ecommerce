import graphene
from graphene_django import DjangoObjectType

from core.catalogue.models import Product, ProductType

__all__ = ["Query"]


class ProductTypeScheme(DjangoObjectType):
    class Meta:
        model = ProductType


class ProductScheme(DjangoObjectType):
    product_type = graphene.Field(ProductTypeScheme)

    class Meta:
        model = Product


class Query(graphene.ObjectType):
    all_products = graphene.List(ProductScheme)
    all_product_types = graphene.List(ProductTypeScheme)

    @staticmethod
    def resolve_all_products(root, info):
        # We can easily optimize query count in the resolve method
        return Product.objects.select_related("parent", "product_type").prefetch_related('attribute_values').all()

    @staticmethod
    def resolve_all_product_types(root, info):
        return ProductType.objects.all()
