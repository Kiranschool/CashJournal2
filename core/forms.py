from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction, JournalEntry, WishlistItem, Category
from .nlp_utils import categorize_transaction, get_category_suggestions, learn_from_correction

class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'purchase_name', 'reflection', 'purchase_reflection', 'date', 'category', 'transaction_type', 'is_recurring', 'recurring_frequency', 'recurring_end_date']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'purchase_name': forms.TextInput(attrs={'class': 'form-control'}),
            'reflection': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'purchase_reflection': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurring_frequency': forms.Select(attrs={'class': 'form-select'}),
            'recurring_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        
        # Add Bootstrap classes to labels
        for field_name, field in self.fields.items():
            field.label = field.label.title()
            if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    def clean(self):
        cleaned_data = super().clean()
        is_recurring = cleaned_data.get('is_recurring')
        recurring_frequency = cleaned_data.get('recurring_frequency')
        recurring_end_date = cleaned_data.get('recurring_end_date')

        if is_recurring:
            if not recurring_frequency:
                raise forms.ValidationError("Please select a recurring frequency.")
            if not recurring_end_date:
                raise forms.ValidationError("Please select an end date for the recurring transaction.")
            
            # Ensure end date is after start date
            start_date = cleaned_data.get('date')
            if recurring_end_date and start_date and recurring_end_date <= start_date:
                raise forms.ValidationError("End date must be after the start date.")

        return cleaned_data

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['date', 'content', 'transaction']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class WishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['name', 'description', 'estimated_cost', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter estimated cost'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        estimated_cost = cleaned_data.get('estimated_cost')
        
        # Convert amount to USD if user's default currency is not USD
        if estimated_cost and self.user:
            user_currency = self.user.userpreferences.default_currency
            if user_currency != 'USD':
                from .utils import convert_currency
                cleaned_data['estimated_cost'] = convert_currency(estimated_cost, user_currency, 'USD')
        
        return cleaned_data 