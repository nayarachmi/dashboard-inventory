# inventory/management/commands/update_rental_status.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from inventory.models import Rental

class Command(BaseCommand):
    help = 'Update equipment status for expired rentals'

    def handle(self, *args, **kwargs):
        current_date = timezone.now().date()
        expired_rentals = Rental.objects.filter(
            end_date__lt=current_date,
            equipment__position='rented'
        )
        
        updated_count = 0
        for rental in expired_rentals:
            if rental.check_and_update_status():
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} expired rentals'
            )
        )
