import csv
import datetime
import os

# --- Constants for Data Handling ---
CSV_FILE = 'expenses.csv'
FIELDNAMES = ['Date', 'Type', 'Description', 'Category', 'Amount']


def initialize_csv():
    """Creates the CSV file with headers if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()


def get_transactions():
    """Reads all transactions from the CSV file."""
    try:
        with open(CSV_FILE, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except FileNotFoundError:
        return []


def save_all_transactions(transactions):
    """Overwrites the CSV file with the provided list of transactions."""
    with open(CSV_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(transactions)


def search_transactions(keyword="", category="", date_str=""):
    """Filters transactions based on keyword, category, and/or date."""
    all_transactions = get_transactions()
    if not keyword and not category and not date_str:
        return all_transactions

    filtered = []
    for transaction in all_transactions:
        keyword_match = True
        category_match = True
        date_match = True
        if keyword and keyword.lower() not in transaction.get('Description', '').lower():
            keyword_match = False
        if category and category.lower() != transaction.get('Category', '').lower():
            category_match = False
        if date_str and date_str != transaction.get('Date', ''):
            date_match = False
        if keyword_match and category_match and date_match:
            filtered.append(transaction)
    return filtered

def sort_transactions_by_date(transactions, descending=False):
    """Sorts a list of expense dictionaries by date."""
    # The 'YYYY-MM-DD' format can be sorted correctly as strings.
    # The `key` lambda function tells sort() to look at the 'Date' value in each dictionary.
    # The `reverse` parameter controls ascending vs. descending order.
    return sorted(transactions, key=lambda t: t.get('Date', ''), reverse=descending)


def get_summary_text():
    """Generates a summary of income, expenses, and balance as plain text."""
    transactions = get_transactions()
    if not transactions:
        return "No transactions to summarize."

    total_income = 0.0
    total_expense = 0.0
    income_categories = {}
    expense_categories = {}

    for row in transactions:
        try:
            # Check for empty or invalid data BEFORE trying to use it
            amount_str = row.get('Amount')
            category = row.get('Category')

            if not amount_str or not category:
                continue  # Skip rows with missing essential data

            amount = float(amount_str)
            trans_type = row.get('Type', 'Expense')

            if trans_type == 'Income':
                total_income += amount
                income_categories[category] = income_categories.get(category, 0) + amount
            else:
                total_expense += amount
                expense_categories[category] = expense_categories.get(category, 0) + amount
        except (ValueError, KeyError, TypeError):
            # This will now catch errors from float() or other unexpected issues
            continue
        except (ValueError, KeyError, TypeError):
            continue

    # ---Calculate net_balance here ---
    net_balance = total_income - total_expense

    # Build the summary
    summary = "--- Overall Summary ---\n"
    summary += f"{'Total Income:':<18} RM {total_income:>10.2f}\n"
    summary += f"{'Total Expenses:':<18} RM {total_expense:>10.2f}\n"
    summary += "----------------------------------\n"
    # --- FIX: Use the net_balance variable ---
    summary += f"{'Net Balance:':<18} RM {net_balance:>10.2f}\n\n"

    summary += "--- Income by Category ---\n"
    if not income_categories:
        summary += "No income recorded.\n"
    else:
        for category, total in sorted(income_categories.items()):
            summary += f"{category:<18}: RM {total:>9.2f}\n"

    summary += "\n--- Expenses by Category ---\n"
    if not expense_categories:
        summary += "No expenses recorded.\n"
    else:
        for category, total in sorted(expense_categories.items()):
            summary += f"{category:<18}: RM {total:>9.2f}\n"

    return summary