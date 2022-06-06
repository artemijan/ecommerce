import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from core.catalogue.models import Product, ProductAttributeValue, ProductType

__all__ = ["Query"]


class ProductAttributeValueScheme(graphene.ObjectType):
    attribute = graphene.String(required=False)
    value = graphene.String(required=False)

    @staticmethod
    def resolve_attribute(attr_val: ProductAttributeValue, _info: ResolveInfo):
        return attr_val.attribute.code

    @staticmethod
    def resolve_value(attr_val: ProductAttributeValue, _info: ResolveInfo):
        return str(attr_val.value)


class ProductTypeScheme(DjangoObjectType):
    class Meta:
        model = ProductType


class ProductScheme(DjangoObjectType):
    product_type = graphene.Field(ProductTypeScheme)
    attribute_values = graphene.List(ProductAttributeValueScheme)

    class Meta:
        model = Product

    @staticmethod
    def resolve_attribute_values(product: Product, _info: ResolveInfo):
        return product.attribute_values.all()


class Query(graphene.ObjectType):
    all_products = graphene.List(ProductScheme)
    all_product_types = graphene.List(ProductTypeScheme)

    @staticmethod
    def resolve_all_products(_root, _info):
        # We can easily optimize query count in the resolve method
        return (
            Product.objects.select_related("parent", "product_type")
            .prefetch_related("attribute_values")
            .all()
        )

    @staticmethod
    def resolve_all_product_types(_root, _info):
        return ProductType.objects.all()
