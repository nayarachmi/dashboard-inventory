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
    ktp_photo = models.ImageField(upload_to='ktp_photos/', null=True, blank=True)

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
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    
    # Tambahan field baru
    promo_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_returned = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Menghitung total_price dengan mempertimbangkan promo
        base_price = self.equipment.monthly_rental_price * self.rental_duration
        self.total_price = base_price - self.promo_discount + self.shipping_cost
        super().save(*args, **kwargs)



from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    date = models.DateField(default=timezone.now)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.TextField()
    
    # Optional relations to existing models
    rental = models.ForeignKey(
        'Rental', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='financial_transactions'
    )
    customer = models.ForeignKey(
        'Customer', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='financial_transactions'
    )
    equipment = models.ForeignKey(
        'Equipment', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='financial_transactions'
    )

    # For expenses only
    expense_category = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        choices=[
            ('maintenance', 'Equipment Maintenance'),
            ('purchase', 'Equipment Purchase'),
            ('operational', 'Operational Costs'),
            ('other', 'Other Expenses')
        ]
    )
    
    # For rental payments
    payment_period_start = models.DateField(null=True, blank=True)
    payment_period_end = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.date}"

    def save(self, *args, **kwargs):
        # If this is a rental payment, automatically set the payment period
        if self.rental and self.transaction_type == 'income':
            if not self.payment_period_start:
                self.payment_period_start = self.rental.start_date
            if not self.payment_period_end:
                months = self.rental.rental_duration
                self.payment_period_end = self.payment_period_start + timezone.timedelta(days=30*months)
        super().save(*args, **kwargs)

class RentalPayment(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_for_month = models.DateField()  # The month this payment covers
    transaction = models.OneToOneField(
        FinancialTransaction, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        # Create corresponding FinancialTransaction if it doesn't exist
        if not self.transaction:
            self.transaction = FinancialTransaction.objects.create(
                transaction_type='income',
                amount=self.amount_paid,
                description=f"Rental payment for {self.rental.equipment} by {self.rental.customer}",
                rental=self.rental,
                customer=self.rental.customer,
                equipment=self.rental.equipment,
                payment_period_start=self.payment_for_month,
                payment_period_end=self.payment_for_month + timezone.timedelta(days=30)
            )
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-payment_date']
        
    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.rental} on {self.payment_date}"
    

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    date = models.DateField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    expense_category = models.CharField(max_length=50, blank=True, null=True)
    
    # Optional relations
    rental = models.ForeignKey('Rental', on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True)
    equipment = models.ForeignKey('Equipment', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.description} - Rp{self.amount}"
    
    from django.db import models
from django.utils import timezone

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    expense_category = models.ForeignKey(
        ExpenseCategory, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Related entities
    rental = models.ForeignKey(
        'Rental',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    equipment = models.ForeignKey(
        'Equipment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.description} - Rp{self.amount}"