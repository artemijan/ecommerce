# Generated by Django 4.0.5 on 2022-06-06 14:28

import core.common.abstract
import core.common.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="AttributeOptionGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128, verbose_name="Name")),
            ],
            options={
                "verbose_name": "Attribute option group",
                "verbose_name_plural": "Attribute option groups",
            },
            bases=(core.common.abstract.AbstractAuditableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("path", models.CharField(max_length=255, unique=True)),
                ("depth", models.PositiveIntegerField()),
                ("numchild", models.PositiveIntegerField(default=0)),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=255, verbose_name="Name"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        max_length=255,
                        null=True,
                        upload_to="categories",
                        verbose_name="Image",
                    ),
                ),
                ("slug", models.SlugField(max_length=255, verbose_name="Slug")),
            ],
            options={
                "verbose_name": "Category",
                "verbose_name_plural": "Categories",
                "ordering": ["path"],
            },
            bases=(models.Model, core.common.abstract.AbstractAuditableModelMixin),
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Product name")),
                (
                    "image",
                    models.ImageField(
                        null=True, upload_to="", verbose_name="Product image"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="Product description"
                    ),
                ),
                ("upc", models.CharField(max_length=255, verbose_name="Product upc")),
                (
                    "contains_hazmat",
                    models.BooleanField(
                        default=False,
                        verbose_name="Product contains hazardous materials",
                    ),
                ),
                (
                    "rating",
                    models.FloatField(editable=False, null=True, verbose_name="Rating"),
                ),
                (
                    "is_discountable",
                    models.BooleanField(
                        default=True,
                        help_text="This flag indicates if this product can be used in an offer or not",
                        verbose_name="Is discountable?",
                    ),
                ),
            ],
            bases=(core.common.abstract.AbstractAuditableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ProductType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128, verbose_name="Name")),
                (
                    "slug",
                    django_extensions.db.fields.AutoSlugField(
                        blank=True,
                        editable=False,
                        max_length=128,
                        populate_from="name",
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "requires_shipping",
                    models.BooleanField(
                        default=True, verbose_name="Requires shipping?"
                    ),
                ),
                (
                    "track_stock",
                    models.BooleanField(
                        default=True, verbose_name="Track stock levels?"
                    ),
                ),
            ],
            options={
                "verbose_name": "Product class",
                "verbose_name_plural": "Product classes",
                "ordering": ["name"],
            },
            bases=(core.common.abstract.AbstractAuditableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ProductCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalogue.category",
                        verbose_name="Category",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalogue.product",
                        verbose_name="Product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product category",
                "verbose_name_plural": "Product categories",
                "ordering": ["product", "category"],
                "unique_together": {("product", "category")},
            },
        ),
        migrations.CreateModel(
            name="ProductAttribute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128, verbose_name="Name")),
                (
                    "code",
                    models.SlugField(
                        max_length=128,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Code can only contain the letters a-z, A-Z, "
                                "digits, and underscores, and can't start with a digit.",
                                regex="^[a-zA-Z_][0-9a-zA-Z_]*$",
                            ),
                            core.common.validators.non_python_keyword,
                        ],
                        verbose_name="Code",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("text", "Text"),
                            ("integer", "Integer"),
                            ("boolean", "True / False"),
                            ("float", "Float"),
                            ("richtext", "Rich Text"),
                            ("date", "Date"),
                            ("datetime", "Datetime"),
                            ("option", "Option"),
                            ("multi_option", "Multi Option"),
                            ("entity", "Entity"),
                            ("file", "File"),
                            ("image", "Image"),
                        ],
                        default="text",
                        max_length=20,
                        verbose_name="Type",
                    ),
                ),
                (
                    "required",
                    models.BooleanField(default=False, verbose_name="Required"),
                ),
                (
                    "option_group",
                    models.ForeignKey(
                        blank=True,
                        help_text='Select an option group if using type "Option" or "Multi Option"',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalogue.attributeoptiongroup",
                        verbose_name="Option Group",
                    ),
                ),
                (
                    "product_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attributes",
                        to="catalogue.producttype",
                        verbose_name="Product type",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product attribute",
                "verbose_name_plural": "Product attributes",
                "ordering": ["code"],
            },
            bases=(core.common.abstract.AbstractAuditableModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name="product",
            name="categories",
            field=models.ManyToManyField(
                through="catalogue.ProductCategory",
                to="catalogue.category",
                verbose_name="Categories",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="parent",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="catalogue.product",
                verbose_name="Parent product",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="product_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="catalogue.producttype",
                verbose_name="Product type",
            ),
        ),
        migrations.CreateModel(
            name="AttributeOption",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("option", models.CharField(max_length=255, verbose_name="Option")),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="options",
                        to="catalogue.attributeoptiongroup",
                        verbose_name="Group",
                    ),
                ),
            ],
            options={
                "verbose_name": "Attribute option",
                "verbose_name_plural": "Attribute options",
                "unique_together": {("group", "option")},
            },
            bases=(core.common.abstract.AbstractAuditableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ProductAttributeValue",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "value_text",
                    models.TextField(blank=True, null=True, verbose_name="Text"),
                ),
                (
                    "value_integer",
                    models.IntegerField(blank=True, null=True, verbose_name="Integer"),
                ),
                (
                    "value_boolean",
                    models.BooleanField(blank=True, null=True, verbose_name="Boolean"),
                ),
                (
                    "value_float",
                    models.FloatField(blank=True, null=True, verbose_name="Float"),
                ),
                (
                    "value_richtext",
                    models.TextField(blank=True, null=True, verbose_name="Richtext"),
                ),
                (
                    "value_date",
                    models.DateField(blank=True, null=True, verbose_name="Date"),
                ),
                (
                    "value_datetime",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="DateTime"
                    ),
                ),
                (
                    "value_file",
                    models.FileField(
                        blank=True, max_length=255, null=True, upload_to=""
                    ),
                ),
                (
                    "value_image",
                    models.ImageField(
                        blank=True, max_length=255, null=True, upload_to=""
                    ),
                ),
                (
                    "entity_object_id",
                    models.PositiveIntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "attribute",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalogue.productattribute",
                        verbose_name="Attribute",
                    ),
                ),
                (
                    "entity_content_type",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attribute_values",
                        to="catalogue.product",
                        verbose_name="Product",
                    ),
                ),
                (
                    "value_multi_option",
                    models.ManyToManyField(
                        blank=True,
                        related_name="multi_valued_attribute_values",
                        to="catalogue.attributeoption",
                        verbose_name="Value multi option",
                    ),
                ),
                (
                    "value_option",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalogue.attributeoption",
                        verbose_name="Value option",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product attribute value",
                "verbose_name_plural": "Product attribute values",
                "unique_together": {("attribute", "product")},
            },
            bases=(core.common.abstract.AbstractAuditableModelMixin, models.Model),
        ),
    ]
