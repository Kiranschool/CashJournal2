from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#000000")  # Hex color code
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    PURCHASE_REFLECTIONS = [
        ('happy', 'I\'m happy with this purchase'),
        ('regret', 'I regret this purchase'),
        ('undecided', 'I am undecided'),
    ]

    RECURRING_FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Every 2 Weeks'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Every 3 Months'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    purchase_name = models.CharField(max_length=200, help_text="Name of the purchase (e.g., 'Coffee', 'Netflix')")
    reflection = models.TextField(blank=True, help_text="Your thoughts and reflections about this purchase")
    purchase_reflection = models.CharField(max_length=10, choices=PURCHASE_REFLECTIONS, null=True, blank=True, help_text="Do you regret this purchase?")
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    image = models.ImageField(upload_to='transaction_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Recurring transaction fields
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=10,
        choices=RECURRING_FREQUENCIES,
        null=True,
        blank=True
    )
    recurring_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    parent_transaction = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recurring_instances'
    )

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.purchase_name} - {self.amount}"

    def get_purchase_reflection_display(self):
        return dict(self.PURCHASE_REFLECTIONS).get(self.purchase_reflection, '')

    def get_recurring_frequency_display(self):
        return dict(self.RECURRING_FREQUENCIES).get(self.recurring_frequency, '')

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField()
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Journal Entry - {self.date}"

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    priority = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_currency = models.CharField(max_length=3, default='USD')
    notification_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"

@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create UserPreferences when a new user is created"""
    if created:
        UserPreferences.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_preferences(sender, instance, **kwargs):
    """Save UserPreferences when user is saved"""
    instance.userpreferences.save()
