# Generated by Django 4.0.5 on 2022-06-06 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0002_remove_productattribute_option_group_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="producttype",
            options={
                "ordering": ["name"],
                "verbose_name": "Product type",
                "verbose_name_plural": "Product types",
            },
        ),
        migrations.AlterField(
            model_name="product",
            name="parent",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="catalogue.product",
                verbose_name="Parent product",
            ),
        ),
    ]
