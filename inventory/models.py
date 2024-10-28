# inventory/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class Owner(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField()

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(default=000,max_length=15)
    whatsapp_number = models.CharField(default=000,max_length=15)
    spouse_phone_number = models.CharField(default=000,max_length=15, null=True, blank=True)
    ktp_address = models.TextField(default='Alamat KTP belum diisi')
    shipping_address = models.TextField(default='Alamat Pengiriman belum diisi')
    maps_link = models.URLField(default='https://example.com')
    transfer_receipt = models.FileField(upload_to='receipts/', validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])
    refund_account_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

class Equipment(models.Model):
    POSITION_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Disewa'),
        ('damaged', 'Rusak'),
    ]

    inventory_code = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    inventory_number = models.CharField(max_length=100)
    monthly_rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='available')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.brand} - {self.inventory_code}"
    
    from django.db import models

from django.db import models

class Rental(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rental_duration = models.IntegerField()  # Dalam bulan
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    rental_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(default = timezone.now)  # Tanggal mulai sewa
    end_date = models.DateField(default = timezone.now)    # Tanggal selesai sewa

    def save(self, *args, **kwargs):
        # Menghitung total_price
        self.total_price = self.equipment.monthly_rental_price * self.rental_duration
        super().save(*args, **kwargs)