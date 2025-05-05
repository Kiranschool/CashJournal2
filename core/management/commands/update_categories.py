from django.core.management.base import BaseCommand
from core.models import Category
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Updates the categories to match the NLP categories'

    def handle(self, *args, **kwargs):
        # Get or create the default user for system categories
        default_user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'is_staff': True,
                'is_superuser': True
            }
        )

        # Define the new categories
        new_categories = [
            'Food & Dining',
            'Transportation',
            'Shopping',
            'Entertainment',
            'Bills & Utilities',
            'Health & Fitness',
            'Travel',
            'Education',
            'Personal Care',
            'Other'
        ]

        # Delete existing categories
        Category.objects.all().delete()

        # Create new categories
        for category_name in new_categories:
            Category.objects.create(
                name=category_name,
                user=default_user,
                is_default=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}')) 