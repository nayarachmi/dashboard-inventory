# Generated by Django 5.1.2 on 2024-10-28 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_delete_financialrecord_remove_customer_ktp_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='ktp_address',
            field=models.TextField(default='Alamat KTP belum diisi'),
        ),
        migrations.AddField(
            model_name='customer',
            name='maps_link',
            field=models.URLField(default='https://example.com'),
        ),
        migrations.AddField(
            model_name='customer',
            name='refund_account_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='rental_duration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='rental_history',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='shipping_address',
            field=models.TextField(default='Alamat Pengiriman belum diisi'),
        ),
        migrations.AddField(
            model_name='customer',
            name='spouse_phone_number',
            field=models.CharField(blank=True, default=0, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='transfer_receipt',
            field=models.ImageField(blank=True, null=True, upload_to='receipts/'),
        ),
        migrations.AddField(
            model_name='customer',
            name='whatsapp_number',
            field=models.CharField(default=0, max_length=15),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone_number',
            field=models.CharField(default=0, max_length=15),
        ),
    ]
