# inventory/forms.py
from django import forms
from .models import Equipment, Owner, Customer, Rental
from django.utils import timezone

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = '__all__'

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = '__all__'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'rental_history': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_receipt'].required = False

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['equipment', 'customer', 'start_date', 'rental_duration']  # Exclude end_date from fields

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        rental_duration = cleaned_data.get('rental_duration')

        if start_date and rental_duration:
            # Calculate end_date based on start_date and rental_duration
            cleaned_data['end_date'] = start_date + timezone.timedelta(days=rental_duration * 30)  # Assuming 30 days in a month

        return cleaned_data