from datetime import date, datetime
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.validators import RegexValidator
from django.db import models
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from core.common.abstract import AbstractAuditableModelMixin
from core.common.validators import non_python_keyword

__all__ = [
    "ProductAttribute",
    "ProductAttributeValue",
]


class ProductAttribute(AbstractAuditableModelMixin, models.Model):
    """
    Defines an attribute for a product class. (For example, number_of_pages for
    a 'book' class)
    """

    product_type = models.ForeignKey(
        "catalogue.ProductType",
        blank=True,
        on_delete=models.CASCADE,
        related_name="attributes",
        null=True,
        verbose_name=_("Product type"),
    )
    name = models.CharField(_("Name"), max_length=128)
    code = models.SlugField(
        _("Code"),
        max_length=128,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z_][0-9a-zA-Z_]*$",
                message=_(
                    "Code can only contain the letters a-z, A-Z, digits, "
                    "and underscores, and can't start with a digit."
                ),
            ),
            non_python_keyword,
        ],
    )

    # Attribute types
    TEXT = "text"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    FLOAT = "float"
    RICHTEXT = "richtext"
    DATE = "date"
    DATETIME = "datetime"
    OPTION = "option"
    MULTI_OPTION = "multi_option"
    TYPE_CHOICES = (
        (TEXT, _("Text")),
        (INTEGER, _("Integer")),
        (BOOLEAN, _("True / False")),
        (FLOAT, _("Float")),
        (RICHTEXT, _("Rich Text")),
        (DATE, _("Date")),
        (DATETIME, ("Datetime")),
    )
    type = models.CharField(
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES[0][0],
        max_length=20,
        verbose_name=_("Type"),
    )

    required = models.BooleanField(_("Required"), default=False)

    class Meta:
        app_label = "catalogue"
        ordering = ["code"]
        verbose_name = _("Product attribute")
        verbose_name_plural = _("Product attributes")

    def __str__(self):
        return self.name

    def save_value(self, product, value):  # noqa: C901 too complex
        try:
            value_obj = product.attribute_values.get(attribute=self)
        except ProductAttributeValue.DoesNotExist:
            value_obj = ProductAttributeValue.objects.create(
                product=product, attribute=self
            )
        if value is None or value == "":
            value_obj.delete()
            return
        if value != value_obj.value:
            value_obj.value = value
            value_obj.save()

    def validate_value(self, value):
        validator = getattr(self, f"_validate_{self.type}")
        validator(value)

    # Validators
    def _validate_text(self, value):
        if not isinstance(value, str):
            raise ValidationError(_("Must be str"))

    _validate_richtext = _validate_text

    def _validate_float(self, value):
        try:
            float(value)
        except ValueError as ex:
            raise ValidationError(_("Must be a float")) from ex

    def _validate_integer(self, value):
        try:
            int(value)
        except ValueError as ex:
            raise ValidationError(_("Must be an integer")) from ex

    def _validate_date(self, value):
        if not isinstance(value, (datetime, date)):
            raise ValidationError(_("Must be a date or datetime"))

    def _validate_datetime(self, value):
        if not isinstance(value, datetime):
            raise ValidationError(_("Must be a datetime"))

    def _validate_boolean(self, value):
        if not isinstance(value, bool):
            raise ValidationError(_("Must be a boolean"))


class ProductAttributeValue(AbstractAuditableModelMixin, models.Model):
    """
    The "through" model for the m2m relationship between catalogue.Product and
    catalogue.ProductAttribute.  This specifies the value of the attribute for
    a particular product

    For example: number_of_pages = 295
    """

    attribute = models.ForeignKey(
        "catalogue.ProductAttribute",
        on_delete=models.CASCADE,
        verbose_name=_("Attribute"),
    )
    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.CASCADE,
        related_name="attribute_values",
        verbose_name=_("Product"),
    )

    value_text = models.TextField(_("Text"), blank=True, null=True)
    value_integer = models.IntegerField(_("Integer"), blank=True, null=True)
    value_boolean = models.BooleanField(_("Boolean"), blank=True, null=True)
    value_float = models.FloatField(_("Float"), blank=True, null=True)
    value_richtext = models.TextField(_("Richtext"), blank=True, null=True)
    value_date = models.DateField(_("Date"), blank=True, null=True)
    value_datetime = models.DateTimeField(_("DateTime"), blank=True, null=True)

    class Meta:
        app_label = "catalogue"
        unique_together = ("attribute", "product")
        verbose_name = _("Product attribute value")
        verbose_name_plural = _("Product attribute values")

    def __str__(self):
        return self.summary()

    @property
    def value(self):
        value = getattr(self, f"value_{self.attribute.type}")
        if hasattr(value, "all"):
            value = value.all()
        return value

    @value.setter
    def value(self, new_value):
        attr_name = f"value_{self.attribute.type}"
        setattr(self, attr_name, new_value)

    def summary(self):
        """
        Gets a string representation of both the attribute and it's value,
        used e.g in product summaries.
        """
        return f"{self.attribute.name}: {self.value_as_text}"

    @property
    def value_as_text(self):
        """
        Returns a string representation of the attribute's value. To customise
        e.g. image attribute values, declare a _image_as_text property and
        return something appropriate.
        """
        property_name = f"_{self.attribute.type}_as_text"
        return getattr(self, property_name, self.value)

    @property
    def _richtext_as_text(self):
        return strip_tags(self.value)

    @property
    def value_as_html(self):
        """
        Returns a HTML representation of the attribute's value. To customise
        e.g. image attribute values, declare a _image_as_html property and
        return e.g. an <img> tag.  Defaults to the _as_text representation.
        """
        property_name = f"_{self.attribute.type}_as_html"
        return getattr(self, property_name, self.value_as_text)

    @property
    def _richtext_as_html(self):
        return mark_safe(self.value)
