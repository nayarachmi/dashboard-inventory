from datetime import date, datetime, timezone
from django.shortcuts import get_object_or_404, render, redirect
from .models import Equipment, ExpenseCategory, Owner, Customer, Rental, Transaction
from .forms import EquipmentForm, OwnerForm, CustomerForm, RentalForm
from django.utils import timezone
from datetime import timedelta


# Dashboard view
# views.py
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

def dashboard_view(request):
    # Inisialisasi queryset dasar
    equipment_list = Equipment.objects.all()
    customer_list = Customer.objects.all()
    rental_list = Rental.objects.all().select_related('equipment', 'customer')
    
    query = request.GET.get('search', '').strip()
    
    if query:
        # Filter Equipment
        equipment_list = equipment_list.filter(
            Q(inventory_code__icontains=query) |
            Q(brand__icontains=query) |
            Q(type__icontains=query) |
            Q(inventory_number__icontains=query)
        )
        
        # Filter Customer
        customer_list = customer_list.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(whatsapp_number__icontains=query)
        )
        
        # Filter Rental
        rental_list = rental_list.filter(
            Q(equipment__brand__icontains=query) |
            Q(equipment__inventory_code__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(total_price__icontains=query)
        )

    # Filter status untuk equipment
    status = request.GET.get('status', '')
    if status:
        equipment_list = equipment_list.filter(position=status)

    # Perhitungan untuk rental yang akan jatuh tempo
    today = timezone.now().date()
    three_days_from_now = today + timedelta(days=3)
    five_days_from_now = today + timedelta(days=5)

    rentals_ending_today = Rental.objects.filter(end_date=today)
    rentals_ending_3_days = Rental.objects.filter(
        end_date__gt=today,
        end_date__lte=three_days_from_now
    )
    rentals_ending_5_days = Rental.objects.filter(
        end_date__gt=three_days_from_now,
        end_date__lte=five_days_from_now
    )

    end_date = request.GET.get('end_date')
    start_date = request.GET.get('start_date')
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = timezone.now()
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = end_date - timedelta(days=30)
    
    # Get all transactions within date range
    transactions = Transaction.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('-date')
    
    # Calculate total income and expenses
    income_total = transactions.filter(
        transaction_type='income'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    expenses_total = transactions.filter(
        transaction_type='expense'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Get expense breakdown by category
    raw_expense_breakdown = transactions.filter(
        transaction_type='expense'
    ).values('expense_category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Calculate percentages
    expense_breakdown = []
    for expense in raw_expense_breakdown:
        percentage = 0
        if expenses_total > 0:
            percentage = (expense['total'] / expenses_total) * 100
            
        expense_breakdown.append({
            'expense_category': expense['expense_category'],
            'total': expense['total'],
            'percentage': round(percentage, 1)
        })
    
    # Calculate net income
    net_income = income_total - expenses_total


    context = {
        'equipment_list': equipment_list,
        'customer_list': customer_list,
        'rental_list': rental_list,
        'rentals_ending_today': rentals_ending_today,
        'rentals_ending_3_days': rentals_ending_3_days,
        'rentals_ending_5_days': rentals_ending_5_days,
        'status': status,
        'search_query': query,
        'start_date': start_date,
        'end_date': end_date,
        'transactions': transactions,
        'total_income': income_total,
        'total_expenses': expenses_total,
        'net_income': net_income,
        'expense_breakdown': expense_breakdown,
    }

    return render(request, 'inventory/dashboard.html', context)

# View for adding new equipment
def add_equipment_view(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EquipmentForm()
    return render(request, 'inventory/add_equipment.html', {'form': form})

# View for adding new owner
def add_owner_view(request):
    if request.method == 'POST':
        form = OwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = OwnerForm()
    return render(request, 'inventory/add_owner.html', {'form': form})

def add_customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES)  # Debug: cek apakah file ada dalam request
            form.save()
            return redirect('dashboard')
        else:
            print(form.errors)  # Debug: cek error form jika ada
    else:
        form = CustomerForm()

    return render(request, 'inventory/add_customer.html', {'form': form})

# View for displaying equipment details
def equipment_detail_view(request, pk):
    equipment = Equipment.objects.get(pk=pk)
    return render(request, 'inventory/equipment_detail.html', {'equipment': equipment})

def edit_equipment(request, id):
    equipment = get_object_or_404(Equipment, id=id)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'inventory/edit_equipment.html', {'form': form})


def edit_equipment(request, id):
    equipment = get_object_or_404(Equipment, id=id)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'inventory/edit_equipment.html', {'form': form})

def delete_equipment(request, id):
    equipment = get_object_or_404(Equipment, id=id)
    equipment.delete()
    return redirect('dashboard')

def edit_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to the dashboard after saving
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'inventory/edit_customer.html', {'form': form})

def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    return redirect('dashboard')

def add_view(request, form_class, template_name, redirect_url):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)  # Include request.FILES for image uploads
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form_class()
    return render(request, template_name, {'form': form})

def add_equipment_view(request):
    return add_view(request, EquipmentForm, 'inventory/add_equipment.html', 'dashboard')

def add_customer_view(request):
    return add_view(request, CustomerForm, 'inventory/add_customer.html', 'dashboard')

def add_owner_view(request):
    return add_view(request, OwnerForm, 'inventory/add_owner.html', 'dashboard')

def add_rental(request):
    if request.method == "POST":
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)  # Don't save yet
            rental.end_date = form.cleaned_data['end_date']  # Set end_date
            rental.save()  # Now save the rental instance
            return redirect('dashboard')  # Redirect to your dashboard
    else:
        form = RentalForm()
    return render(request, 'inventory/add_rental.html', {'form': form})

def rental_detail(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    return render(request, 'inventory/rental_detail.html', {'rental': rental})


def edit_rental(request, id):
    rental = get_object_or_404(Rental, id=id)

    if request.method == 'POST':
        rental.rental_code = request.POST.get('rental_code', rental.equipment.inventory_code)

        # Mengonversi rental_duration ke integer
        try:
            rental.rental_duration = int(request.POST.get('duration', rental.rental_duration))
        except ValueError:
            return render(request, 'inventory/edit_rental.html', {
                'rental': rental,
                'error_message': 'Duration must be a valid number.'
            })

        rental.start_date = request.POST.get('start_date')  # Ambil nilai start_date
        rental.end_date = request.POST.get('end_date')      # Ambil nilai end_date

        customer_name = request.POST.get('customer')
        if customer_name:
            rental.customer.name = customer_name
            rental.customer.save()

        rental.save()  # Simpan perubahan rental
        return redirect('dashboard')  # Ganti dengan nama view untuk dashboard Anda

    return render(request, 'inventory/edit_rental.html', {'rental': rental})

def delete_rental(request, id):
    rental = get_object_or_404(Rental, id=id)
    rental.delete()  # Hapus rental langsung
    return redirect('dashboard')

def customer_detail(request, id):
    customer = get_object_or_404(Customer, id=id)  # Get the customer or return 404
    rental_history = Rental.objects.filter(customer=customer)  # Fetch rentals for the customer
    context = {
        'customer': customer,
        'rental_history': rental_history,
    }
    return render(request, 'inventory/customer_detail.html', context)

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'inventory/customer_list.html', {'customers': customers})



def equipment_detail_view(request, pk):
    # Get the equipment object or return a 404 error if not found
    equipment = get_object_or_404(Equipment, pk=pk)
    
    # Get the current rental for the equipment
    current_rental = Rental.objects.filter(
        equipment=equipment,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()
    
    # Get the rental history for the equipment
    rental_history = Rental.objects.filter(equipment=equipment).order_by('-start_date')
    
    # Prepare the context to pass to the template
    context = {
        'equipment': equipment,
        'current_rental': current_rental,
        'rental_history': rental_history,
    }
    
    return render(request, 'inventory/equipment_detail.html', context)

def inventory_dashboard(request):
    today = timezone.now().date()
    five_days_ago = today - timedelta(days=5)
    three_days_ago = today - timedelta(days=3)

    # Mengambil data rental yang akan jatuh tempo
    rentals_ending_today = Rental.objects.filter(end_date=today)
    rentals_ending_3_days = Rental.objects.filter(end_date__gte=today, end_date__lte=three_days_ago).exclude(end_date=today)
    rentals_ending_5_days = Rental.objects.filter(end_date__gte=three_days_ago, end_date__lte=five_days_ago).exclude(end_date__in=[today, three_days_ago])

    # Menangani filter status
    status = request.GET.get('status', '')
    if status:
        equipment_list = Equipment.objects.filter(position=status)
    else:
        equipment_list = Equipment.objects.all()

    context = {
        'equipment_list': equipment_list,
        'rentals_ending_today': rentals_ending_today,
        'rentals_ending_3_days': rentals_ending_3_days,
        'rentals_ending_5_days': rentals_ending_5_days,
        'status': status,
    }

    return render(request, 'inventory/dashboard.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import FinancialTransaction, RentalPayment, Rental
from .forms import FinancialTransactionForm, RentalPaymentForm

def financial_dashboard(request):
    # Get date range from request parameters or default to current month
    start_date = request.GET.get('start_date', timezone.now().replace(day=1).date())
    end_date = request.GET.get('end_date', timezone.now().date())
    
    # Get all transactions within date range
    transactions = FinancialTransaction.objects.filter(
        date__range=[start_date, end_date]
    )
    
    # Calculate summaries
    total_income = transactions.filter(
        transaction_type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_expenses = transactions.filter(
        transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    net_income = total_income - total_expenses
    
    # Get expense breakdown by category
    expense_breakdown = transactions.filter(
        transaction_type='expense'
    ).values('expense_category').annotate(
        total=Sum('amount')
    )
    
    # Get upcoming rental payments
    upcoming_payments = Rental.objects.filter(
        end_date__gt=timezone.now().date(),
        financial_transactions__isnull=True
    )
    
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'expense_breakdown': expense_breakdown,
        'upcoming_payments': upcoming_payments,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'inventory/dashboard.html', context)


def add_transaction(request):
    if request.method == 'POST':
        try:
            # Get basic transaction data
            transaction_type = request.POST.get('transaction_type')
            date = request.POST.get('date')
            amount = request.POST.get('amount')
            description = request.POST.get('description')
            
            # Create transaction object
            transaction = Transaction(
                transaction_type=transaction_type,
                date=date,
                amount=amount,
                description=description
            )
            
            # Handle expense category for expense transactions
            if transaction_type == 'expense':
                expense_category_id = request.POST.get('expense_category')
                if expense_category_id:
                    transaction.expense_category = get_object_or_404(
                        ExpenseCategory, 
                        id=expense_category_id
                    )
            
            # Handle related entities
            related_to_type = request.POST.get('related_to_type')
            if related_to_type:
                related_id = request.POST.get(related_to_type)
                if related_id:
                    if related_to_type == 'rental':
                        transaction.rental = get_object_or_404(Rental, id=related_id)
                    elif related_to_type == 'customer':
                        transaction.customer = get_object_or_404(Customer, id=related_id)
                    elif related_to_type == 'equipment':
                        transaction.equipment = get_object_or_404(Equipment, id=related_id)
            
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error adding transaction: {str(e)}')
            return redirect('inventory/add_transaction')
    
    # GET request - display form
    context = {
        'expense_categories': ExpenseCategory.objects.all(),
        'customers': Customer.objects.all(),
        'equipment_list': Equipment.objects.all(),
        'rentals': Rental.objects.all(),
        'transaction': {'date': timezone.now()},  # Set default date to today
    }
    return render(request, 'inventory/add_transaction.html', context)

def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    if request.method == 'POST':
        try:
            # Update basic transaction data
            transaction.transaction_type = request.POST.get('transaction_type')
            transaction.date = request.POST.get('date')
            transaction.amount = request.POST.get('amount')
            transaction.description = request.POST.get('description')
            
            # Update expense category
            if transaction.transaction_type == 'expense':
                expense_category_id = request.POST.get('expense_category')
                transaction.expense_category = get_object_or_404(
                    ExpenseCategory, 
                    id=expense_category_id
                ) if expense_category_id else None
            else:
                transaction.expense_category = None
            
            # Update related entities
            related_to_type = request.POST.get('related_to_type')
            # Reset all relations first
            transaction.rental = None
            transaction.customer = None
            transaction.equipment = None
            
            if related_to_type and request.POST.get(related_to_type):
                related_id = request.POST.get(related_to_type)
                if related_to_type == 'rental':
                    transaction.rental = get_object_or_404(Rental, id=related_id)
                elif related_to_type == 'customer':
                    transaction.customer = get_object_or_404(Customer, id=related_id)
                elif related_to_type == 'equipment':
                    transaction.equipment = get_object_or_404(Equipment, id=related_id)
            
            transaction.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error updating transaction: {str(e)}')
    
    context = {
        'transaction': transaction,
        'expense_categories': ExpenseCategory.objects.all(),
        'customers': Customer.objects.all(),
        'equipment_list': Equipment.objects.all(),
        'rentals': Rental.objects.all(),
    }
    return render(request, 'inventory/add_transaction.html', context)

def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    try:
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting transaction: {str(e)}')
    return redirect('dashboard')