from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Transaction

class Command(BaseCommand):
    help = 'Process recurring transactions and create new instances'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Get all active recurring transactions
        recurring_transactions = Transaction.objects.filter(
            is_recurring=True,
            is_active=True,
            recurring_end_date__gte=today
        )

        for transaction in recurring_transactions:
            # Get the last instance of this recurring transaction
            last_instance = Transaction.objects.filter(
                parent_transaction=transaction
            ).order_by('-date').first() or transaction

            # Calculate next date based on frequency
            next_date = self.get_next_date(last_instance.date, transaction.recurring_frequency)
            
            # If next date is today or in the past and before end date, create new instance
            if next_date <= today and next_date <= transaction.recurring_end_date:
                # Create new transaction instance
                new_transaction = Transaction.objects.create(
                    user=transaction.user,
                    amount=transaction.amount,
                    purchase_name=transaction.purchase_name,
                    reflection=transaction.reflection,
                    purchase_reflection=transaction.purchase_reflection,
                    date=next_date,
                    category=transaction.category,
                    transaction_type=transaction.transaction_type,
                    image=transaction.image,
                    is_recurring=True,
                    recurring_frequency=transaction.recurring_frequency,
                    recurring_end_date=transaction.recurring_end_date,
                    is_active=True,
                    parent_transaction=transaction
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created recurring transaction: {new_transaction.purchase_name} for {new_transaction.date}'
                    )
                )

    def get_next_date(self, current_date, frequency):
        """Calculate the next date based on frequency."""
        if frequency == 'daily':
            return current_date + timedelta(days=1)
        elif frequency == 'weekly':
            return current_date + timedelta(weeks=1)
        elif frequency == 'biweekly':
            return current_date + timedelta(weeks=2)
        elif frequency == 'monthly':
            # Handle month transitions
            if current_date.month == 12:
                return current_date.replace(year=current_date.year + 1, month=1)
            return current_date.replace(month=current_date.month + 1)
        elif frequency == 'quarterly':
            # Add 3 months
            new_month = current_date.month + 3
            new_year = current_date.year
            if new_month > 12:
                new_month -= 12
                new_year += 1
            return current_date.replace(year=new_year, month=new_month)
        elif frequency == 'yearly':
            return current_date.replace(year=current_date.year + 1)
        return current_date 