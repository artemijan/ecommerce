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
    "AttributeOptionGroup",
    "AttributeOption",
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
    ENTITY = "entity"
    FILE = "file"
    IMAGE = "image"
    TYPE_CHOICES = (
        (TEXT, _("Text")),
        (INTEGER, _("Integer")),
        (BOOLEAN, _("True / False")),
        (FLOAT, _("Float")),
        (RICHTEXT, _("Rich Text")),
        (DATE, _("Date")),
        (DATETIME, ("Datetime")),
        (OPTION, _("Option")),
        (MULTI_OPTION, _("Multi Option")),
        (ENTITY, _("Entity")),
        (FILE, _("File")),
        (IMAGE, _("Image")),
    )
    type = models.CharField(
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES[0][0],
        max_length=20,
        verbose_name=_("Type"),
    )

    option_group = models.ForeignKey(
        "catalogue.AttributeOptionGroup",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Option Group"),
        help_text=_('Select an option group if using type "Option" or "Multi Option"'),
    )
    required = models.BooleanField(_("Required"), default=False)

    class Meta:
        app_label = "catalogue"
        ordering = ["code"]
        verbose_name = _("Product attribute")
        verbose_name_plural = _("Product attributes")

    def __str__(self):
        return self.name

    @property
    def is_option(self):
        return self.type == self.OPTION

    @property
    def is_multi_option(self):
        return self.type == self.MULTI_OPTION

    @property
    def is_file(self):
        return self.type in [self.FILE, self.IMAGE]

    def save_value(self, product, value):  # noqa: C901 too complex
        try:
            value_obj = product.attribute_values.get(attribute=self)
        except ProductAttributeValue.DoesNotExist:
            # FileField uses False for announcing deletion of the file
            # not creating a new value
            delete_file = self.is_file and value is False
            if value is None or value == "" or delete_file:
                return
            value_obj = ProductAttributeValue.objects.create(
                product=product, attribute=self
            )

        if self.is_file:
            # File fields in Django are treated differently, see
            # django.db.models.fields.FileField and method save_form_data
            if value is None:
                # No change
                return
            elif value is False:
                # Delete file
                value_obj.delete()
            else:
                # New uploaded file
                value_obj.value = value
                value_obj.save()
        elif self.is_multi_option:
            # ManyToMany fields are handled separately
            if value is None:
                value_obj.delete()
                return
            try:
                count = value.count()
            except (AttributeError, TypeError):
                count = len(value)
            if count == 0:
                value_obj.delete()
            else:
                value_obj.value = value
                value_obj.save()
        else:
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
        except ValueError:
            raise ValidationError(_("Must be a float"))

    def _validate_integer(self, value):
        try:
            int(value)
        except ValueError:
            raise ValidationError(_("Must be an integer"))

    def _validate_date(self, value):
        if not isinstance(value, (datetime, date)):
            raise ValidationError(_("Must be a date or datetime"))

    def _validate_datetime(self, value):
        if not isinstance(value, datetime):
            raise ValidationError(_("Must be a datetime"))

    def _validate_boolean(self, value):
        if not isinstance(value, bool):
            raise ValidationError(_("Must be a boolean"))

    def _validate_entity(self, value):
        if not isinstance(value, models.Model):
            raise ValidationError(_("Must be a model instance"))

    def _validate_multi_option(self, value):
        try:
            values = iter(value)
        except TypeError as ex:
            raise ValidationError(
                _("Must be a list or AttributeOption queryset")
            ) from ex
        # Validate each value as if it were an option
        # Pass in valid_values so that the DB isn't hit multiple times per iteration
        valid_values = self.option_group.options.values_list("option", flat=True)
        for val in values:
            self._validate_option(val, valid_values=valid_values)

    def _validate_option(self, value, valid_values=None):
        if not isinstance(value, AttributeOption):
            raise ValidationError(_("Must be an AttributeOption model object instance"))
        if not value.pk:
            raise ValidationError(_("AttributeOption has not been saved yet"))
        if valid_values is None:
            valid_values = self.option_group.options.values_list("option", flat=True)
        if value.option not in valid_values:
            raise ValidationError(
                _("%(enum)s is not a valid choice for %(attr)s")
                % {"enum": value, "attr": self}
            )

    def _validate_file(self, value):
        if value and not isinstance(value, File):
            raise ValidationError(_("Must be a file field"))

    _validate_image = _validate_file


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
    value_multi_option = models.ManyToManyField(
        "catalogue.AttributeOption",
        blank=True,
        related_name="multi_valued_attribute_values",
        verbose_name=_("Value multi option"),
    )
    value_option = models.ForeignKey(
        "catalogue.AttributeOption",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Value option"),
    )
    value_file = models.FileField(max_length=255, blank=True, null=True)
    value_image = models.ImageField(max_length=255, blank=True, null=True)
    value_entity = GenericForeignKey("entity_content_type", "entity_object_id")

    entity_content_type = models.ForeignKey(
        ContentType, blank=True, editable=False, on_delete=models.CASCADE, null=True
    )
    entity_object_id = models.PositiveIntegerField(
        null=True, blank=True, editable=False
    )

    def _get_value(self):
        value = getattr(self, f"value_{self.attribute.type}")
        if hasattr(value, "all"):
            value = value.all()
        return value

    def _set_value(self, new_value):
        attr_name = f"value_{self.attribute.type}"

        if self.attribute.is_option and isinstance(new_value, str):
            # Need to look up instance of AttributeOption
            new_value = self.attribute.option_group.options.get(option=new_value)
        elif self.attribute.is_multi_option:
            getattr(self, attr_name).set(new_value)
            return

        setattr(self, attr_name, new_value)
        return

    value = property(_get_value, _set_value)

    class Meta:
        app_label = "catalogue"
        unique_together = ("attribute", "product")
        verbose_name = _("Product attribute value")
        verbose_name_plural = _("Product attribute values")

    def __str__(self):
        return self.summary()

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
    def _multi_option_as_text(self):
        return ", ".join(str(option) for option in self.value_multi_option.all())

    @property
    def _richtext_as_text(self):
        return strip_tags(self.value)

    @property
    def _entity_as_text(self):
        """
        Returns the unicode representation of the related model. You likely
        want to customise this (and maybe _entity_as_html) if you use entities.
        """
        return str(self.value)

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


class AttributeOptionGroup(AbstractAuditableModelMixin, models.Model):
    """
    Defines a group of options that collectively may be used as an
    attribute type

    For example, Language
    """

    name = models.CharField(_("Name"), max_length=128)

    class Meta:
        app_label = "catalogue"
        verbose_name = _("Attribute option group")
        verbose_name_plural = _("Attribute option groups")

    def __str__(self):
        return self.name

    @property
    def option_summary(self):
        options = [o.option for o in self.options.all()]
        return ", ".join(options)


class AttributeOption(AbstractAuditableModelMixin, models.Model):
    """
    Provides an option within an option group for an attribute type
    Examples: In a Language group, English, Greek, French
    """

    group = models.ForeignKey(
        "catalogue.AttributeOptionGroup",
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name=_("Group"),
    )
    option = models.CharField(_("Option"), max_length=255)

    class Meta:
        app_label = "catalogue"
        unique_together = ("group", "option")
        verbose_name = _("Attribute option")
        verbose_name_plural = _("Attribute options")

    def __str__(self):
        return self.option
