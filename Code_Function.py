import csv
import datetime
import os

# --- Constants for Data Handling ---
CSV_FILE = 'expenses.csv'
FIELDNAMES = ['Date', 'Description', 'Category', 'Amount']


def initialize_csv():
    """Creates the CSV file with headers if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()


def get_expenses():
    """Reads all expenses from the CSV file and returns them as a list of dicts."""
    try:
        with open(CSV_FILE, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except FileNotFoundError:
        return []


def save_all_expenses(expenses):
    """Overwrites the CSV file with the provided list of expenses."""
    with open(CSV_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(expenses)


def search_expenses(keyword="", category="", date_str=""):
    """Filters expenses based on keyword, category, and/or date."""
    all_expenses = get_expenses()

    # If no search term is provided, return all expenses
    if not keyword and not category and not date_str:
        return all_expenses

    filtered_expenses = []
    for expense in all_expenses:
        # Set up match flags for an "AND" search
        keyword_match = True
        category_match = True
        date_match = True

        # Check keyword (case-insensitive search in description)
        if keyword:
            if keyword.lower() not in expense.get('Description', '').lower():
                keyword_match = False

        # Check category (case-insensitive exact match)
        if category:
            if category.lower() != expense.get('Category', '').lower():
                category_match = False

        # Check date (exact match)
        if date_str:
            if date_str != expense.get('Date', ''):
                date_match = False

        # If all criteria are met, add the expense to the list
        if keyword_match and category_match and date_match:
            filtered_expenses.append(expense)

    return filtered_expenses

def get_summary_text():
    """Generates a summary string of expenses by category and month."""
    expenses = get_expenses()
    if not expenses:
        return "No expenses to summarize."

    category_totals = {}
    monthly_totals = {}

    for row in expenses:
        try:
            amount = float(row['Amount'])
            category = row['Category']
            date = datetime.datetime.strptime(row['Date'], '%Y-%m-%d')
            month_year = date.strftime('%Y-%m')

            category_totals[category] = category_totals.get(category, 0) + amount
            monthly_totals[month_year] = monthly_totals.get(month_year, 0) + amount
        except (ValueError, KeyError, TypeError):
            continue  # Skip malformed rows

    summary = "--- Spending by Category ---\n"
    for category, total in sorted(category_totals.items()):
        summary += f"{category:<15}: RM{total:9.2f}\n"

    summary += "\n--- Spending by Month ---\n"
    for month, total in sorted(monthly_totals.items()):
        summary += f"{month:<15}: RM{total:9.2f}\n"

    return summary