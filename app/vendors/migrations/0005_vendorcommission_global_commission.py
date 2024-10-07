# Generated by Django 4.2.5 on 2024-01-20 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0004_remove_vendorcommission_value"),
    ]

    operations = [
        migrations.AddField(
            model_name="vendorcommission",
            name="commission",
            field=models.FloatField(blank=True, null=True, verbose_name="Commission (%)"),
        ),
    ]
