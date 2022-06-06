from django.contrib import admin

# Register your models here.
from core.catalogue.models import Product, ProductAttribute, ProductAttributeValue, ProductType


class AttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute


class ProductAdmin(admin.ModelAdmin):
    inlines = [AttributeValueInline, ]


class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [ProductAttributeInline, ]


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductType, ProductTypeAdmin)
