# inventory/forms.py
from django import forms
from .models import Equipment, Owner, Customer, Rental
from django.utils import timezone

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = '__all__'
    
    def to_json(self):
        return {
            'id': self.id,
            'monthly_rental_price': 
            
            float(self.monthly_rental_price)
        }

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = '__all__'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone_number', 'whatsapp_number', 
                 'spouse_phone_number', 'ktp_address', 'shipping_address', 
                 'maps_link', 'transfer_receipt', 'refund_account_number', 
                 'ktp_photo']
        widgets = {
            'rental_history': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_receipt'].required = False

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['equipment', 'customer', 'rental_duration', 'start_date', 
                 'promo_discount', 'shipping_cost', 'deposit_amount']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        rental_duration = cleaned_data.get('rental_duration')

        if start_date and rental_duration:
            # Calculate end_date based on start_date and rental_duration
            cleaned_data['end_date'] = start_date + timezone.timedelta(days=rental_duration * 30)  # Assuming 30 days in a month

        return cleaned_data
    
from django import forms
from .models import FinancialTransaction, RentalPayment

class FinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = [
            'date',
            'transaction_type',
            'amount',
            'description',
            'rental',
            'customer',
            'equipment',
            'expense_category',
            'payment_period_start',
            'payment_period_end',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'payment_period_start': forms.DateInput(attrs={'type': 'date'}),
            'payment_period_end': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        expense_category = cleaned_data.get('expense_category')
        
        if transaction_type == 'expense' and not expense_category:
            raise forms.ValidationError(
                'Expense category is required for expense transactions.'
            )
        
        return cleaned_data

class RentalPaymentForm(forms.ModelForm):
    class Meta:
        model = RentalPayment
        fields = ['amount_paid', 'payment_date', 'payment_for_month']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_for_month': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        amount_paid = cleaned_data.get('amount_paid')
        
        if amount_paid and amount_paid <= 0:
            raise forms.ValidationError(
                'Payment amount must be greater than zero.'
            )
        
        return cleaned_data
