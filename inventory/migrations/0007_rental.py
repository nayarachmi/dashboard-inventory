# Generated by Django 5.1.2 on 2024-10-28 08:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_remove_customer_rental_history'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rental',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rental_duration', models.IntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('rental_date', models.DateField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.customer')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.equipment')),
            ],
        ),
    ]
