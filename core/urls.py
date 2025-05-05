from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('', views.HomeView.as_view(), name='home'),
    path('calendar/', views.FinanceCalendarView.as_view(), name='finance_calendar'),
    path('transaction/add/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transaction/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('transaction/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', views.WishlistItemCreateView.as_view(), name='wishlist_item_create'),
    path('wishlist/<int:pk>/edit/', views.WishlistItemUpdateView.as_view(), name='wishlist_item_edit'),
    path('wishlist/<int:pk>/delete/', views.WishlistItemDeleteView.as_view(), name='wishlist_item_delete'),
    path('export-data/', views.ExportDataView.as_view(), name='export_data'),
    path('spending-tracker/', views.SpendingTrackerView.as_view(), name='spending_tracker'),
    path('settings/', views.AccountSettingsView.as_view(), name='account_settings'),
    path('settings/delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('api/category-suggestions/', views.category_suggestions, name='category_suggestions'),
    path('api/similar-transactions/', views.similar_transactions, name='similar_transactions'),
] 