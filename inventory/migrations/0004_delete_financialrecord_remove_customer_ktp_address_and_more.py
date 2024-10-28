# Generated by Django 5.1.2 on 2024-10-28 07:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_remove_equipment_tracking'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FinancialRecord',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='ktp_address',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='maps_link',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='rental_history',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='shipping_address',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='spouse_phone_number',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='whatsapp_number',
        ),
        migrations.AddField(
            model_name='equipment',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.customer'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='position',
            field=models.CharField(choices=[('available', 'Available'), ('rented', 'Disewa'), ('damaged', 'Rusak')], default='available', max_length=10),
        ),
    ]