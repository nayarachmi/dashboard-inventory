# Generated by Django 5.1.2 on 2024-10-28 09:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_rename_rental_price_equipment_monthly_rental_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='rental',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='rental',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
