from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.abstract import AbstractAuditableModelMixin

__all__ = ["Product"]


class Product(AbstractAuditableModelMixin, models.Model):
    name = models.CharField(_("Product name"), max_length=255, null=False, blank=False)
    image = models.ImageField(_("Product image"), null=True, blank=True)
    description = models.TextField(_("Product description"), null=True, blank=True)
    upc = models.CharField(
        _("Product upc"), max_length=255, null=False, blank=False, unique=True
    )
    contains_hazmat = models.BooleanField(
        _("Product contains hazardous materials"), default=False
    )
    """
    For this purpose we can use MP_Node, but in our case we expect to have up to 2 children
    """
    parent = models.ForeignKey(
        "self",
        verbose_name=_("Parent product"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    product_type = models.ForeignKey(
        "catalogue.ProductType",
        verbose_name=_("Product type"),
        related_name="products",
        on_delete=models.CASCADE,
    )
    rating = models.FloatField(_("Rating"), null=True, editable=False)
    categories = models.ManyToManyField(
        "catalogue.Category",
        through="catalogue.ProductCategory",
        verbose_name=_("Categories"),
    )
    is_discountable = models.BooleanField(
        _("Is discountable?"),
        default=True,
        help_text=_(
            "This flag indicates if this product can be used in an offer or not"
        ),
    )

    def __str__(self):
        return f"Product (id:{self.pk}): {self.name}"
