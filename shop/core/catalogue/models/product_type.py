from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.abstract import AbstractAuditableModelMixin
from django_extensions.db.models import AutoSlugField

__all__ = ["ProductType"]


class ProductType(AbstractAuditableModelMixin, models.Model):
    """
    Used for defining options and attributes for a subset of products.
    E.g. Books, DVDs and Toys. A product can only belong to one product class.

    At least one product class must be created when setting up a new
    Oscar deployment.

    Not necessarily equivalent to top-level categories but usually will be.
    """

    name = models.CharField(_("Name"), max_length=128)
    slug = AutoSlugField(_("Slug"), max_length=128, unique=True, populate_from="name")

    #: Some product type don't require shipping (eg digital products) - we use
    #: this field to take some shortcuts in the checkout.
    requires_shipping = models.BooleanField(_("Requires shipping?"), default=True)

    #: Digital products generally don't require their stock levels to be
    #: tracked.
    track_stock = models.BooleanField(_("Track stock levels?"), default=True)

    class Meta:
        app_label = "catalogue"
        ordering = ["name"]
        verbose_name = _("Product class")
        verbose_name_plural = _("Product classes")

    def __str__(self):
        return self.name

    @property
    def has_attributes(self):
        return self.attributes.exists()
