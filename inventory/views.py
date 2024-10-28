from datetime import date, timezone
from django.shortcuts import get_object_or_404, render, redirect
from .models import Equipment, Owner, Customer, Rental
from .forms import EquipmentForm, OwnerForm, CustomerForm, RentalForm
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from django.utils import timezone
from datetime import timedelta


# Dashboard view
def dashboard_view(request):
    equipment_list = Equipment.objects.all()
    customer_list = Customer.objects.all()
    rental_list = Rental.objects.all()
    equipment_list = Equipment.objects.all()
    current_rentals = Rental.objects.filter(end_date__isnull=True)
    today = timezone.now().date()
    five_days_ago = today + timedelta(days=5)
    three_days_ago = today + timedelta(days=3)
    
    query = request.GET.get('search', '')  # Ambil parameter search dari URL

    if query:
        equipment_list = equipment_list.filter(name__icontains=query)  # Sesuaikan field
        customer_list = customer_list.filter(name__icontains=query)    # Sesuaikan field
        rental_list = rental_list.filter(equipment__name__icontains=query)  # Sesuaikan field


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


    return render(request, 'inventory/dashboard.html', {
        'equipment_list': equipment_list,
        'customer_list': customer_list,
        'rental_list': rental_list,
        'rentals_ending_today': rentals_ending_today,
        'rentals_ending_3_days': rentals_ending_3_days,
        'rentals_ending_5_days': rentals_ending_5_days,
        'status': status,
        'search_query': query,
    })

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
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new customer
            return redirect('dashboard')  # Redirect to the dashboard after saving
    else:
        form = CustomerForm()  # Create an empty form for GET requests
    
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


