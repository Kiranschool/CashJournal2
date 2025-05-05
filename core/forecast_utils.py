import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from django.utils import timezone

def prepare_spending_data(transactions):
    """Prepare transaction data for regression analysis."""
    # Group transactions by month and calculate total spending
    monthly_spending = {}
    for transaction in transactions:
        if transaction.transaction_type == 'expense':
            month_key = (transaction.date.year, transaction.date.month)
            monthly_spending[month_key] = monthly_spending.get(month_key, 0) + transaction.amount

    # Convert to sorted list of (month_number, amount) pairs
    months = []
    amounts = []
    for (year, month), amount in sorted(monthly_spending.items()):
        # Convert year and month to a single number (e.g., 2024-01 becomes 202401)
        month_number = year * 100 + month
        months.append(month_number)
        amounts.append(amount)

    return np.array(months).reshape(-1, 1), np.array(amounts)

def predict_future_spending(transactions, months_ahead=3):
    """Predict future spending using linear regression."""
    if not transactions:
        return []

    # Prepare data
    X, y = prepare_spending_data(transactions)
    
    if len(X) < 2:  # Need at least 2 data points for regression
        return []

    # Create and train the model
    model = LinearRegression()
    model.fit(X, y)

    # Get the last month from the data
    last_month = X[-1][0]
    
    # Generate future months
    future_months = []
    future_predictions = []
    
    for i in range(1, months_ahead + 1):
        next_month = last_month + i
        if next_month % 100 > 12:  # Handle month overflow
            next_month = (next_month // 100 + 1) * 100 + 1
        
        future_months.append(next_month)
        prediction = model.predict([[next_month]])[0]
        future_predictions.append(max(0, prediction))  # Ensure non-negative predictions

    # Format predictions with month names
    formatted_predictions = []
    for month_num, amount in zip(future_months, future_predictions):
        year = month_num // 100
        month = month_num % 100
        month_name = datetime(year, month, 1).strftime('%B')
        formatted_predictions.append({
            'month': f"{month_name} {year}",
            'amount': amount
        })

    return formatted_predictions 