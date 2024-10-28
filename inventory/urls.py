# inventory/urls.py
from django.urls import path
from .views import (
    dashboard_view, add_equipment_view, add_owner_view, 
    equipment_detail_view, add_customer_view
)
from .views import edit_equipment, delete_equipment, edit_customer, delete_customer, add_rental, rental_detail, edit_rental, delete_rental, customer_detail, equipment_detail_view, inventory_dashboard


urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('add-equipment/', add_equipment_view, name='add_equipment'),
    path('add-owner/', add_owner_view, name='add_owner'),
    path('add-customer/', add_customer_view, name='add_customer'),
    path('equipment/<int:pk>/', equipment_detail_view, name='equipment_detail'),
    path('equipment/edit/<int:id>/', edit_equipment, name='edit_equipment'),
    path('equipment/delete/<int:id>/', delete_equipment, name='delete_equipment'),
    path('customer/edit/<int:id>/', edit_customer, name='edit_customer'),
    path('customer/delete/<int:id>/', delete_customer, name='delete_customer'),
    path('add_rental/', add_rental, name='add_rental'),
    path('rental/<int:rental_id>/', rental_detail, name='rental_detail'),
    path('edit_rental/<int:id>/', edit_rental, name='edit_rental'),
    path('delete_rental/<int:id>/', delete_rental, name='delete_rental'),
    path('customer/<int:id>/', customer_detail, name='customer_detail'),
    path('equipment/<int:id>/', equipment_detail_view, name='equipment_detail'),
    path('', inventory_dashboard, name='inventory_dashboard'),
]