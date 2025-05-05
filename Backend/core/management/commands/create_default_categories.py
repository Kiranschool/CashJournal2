from django.core.management.base import BaseCommand
from core.models import Category

class Command(BaseCommand):
    help = 'Creates default categories if they do not exist'

    def handle(self, *args, **kwargs):
        default_categories = [
            {'name': 'Food & Dining', 'color': '#FF5733'},
            {'name': 'Transportation', 'color': '#33FF57'},
            {'name': 'Shopping', 'color': '#3357FF'},
            {'name': 'Entertainment', 'color': '#FF33F5'},
            {'name': 'Bills & Utilities', 'color': '#33FFF5'},
            {'name': 'Health & Fitness', 'color': '#F5FF33'},
            {'name': 'Travel', 'color': '#FF8333'},
            {'name': 'Education', 'color': '#338FFF'},
            {'name': 'Personal Care', 'color': '#FF33A1'},
            {'name': 'Other', 'color': '#808080'}
        ]

        for category_data in default_categories:
            Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'color': category_data['color'], 'is_default': True}
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully created default categories')) 