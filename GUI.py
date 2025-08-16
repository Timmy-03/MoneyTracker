# --- START OF FILE GUI.py ---

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QDateEdit,
    QLabel, QHeaderView, QMessageBox, QFormLayout
)
from PyQt6.QtCore import QDate, Qt

# --- Import backend functions and constants ---
from Code_Function import (
    get_expenses, save_all_expenses, get_summary_text, FIELDNAMES, search_expenses
)

# --- Main GUI Application Class ---

class ExpenseTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Money Spending Recorder")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # --- Create UI elements ---
        self._create_search_bar()
        self._create_table()
        self._create_input_form()
        self._create_buttons()

        # --- Connect signals to slots ---
        self.table.itemSelectionChanged.connect(self.populate_form_from_selection)

        # --- Initial data load ---
        self.load_expenses()

    def _create_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(FIELDNAMES))
        self.table.setHorizontalHeaderLabels(FIELDNAMES)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layout.addWidget(self.table)

    def _create_input_form(self):
        self.form_layout = QFormLayout()

        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.desc_edit = QLineEdit()
        self.cat_edit = QLineEdit()
        self.amount_edit = QLineEdit()

        self.form_layout.addRow(QLabel("Date:"), self.date_edit)
        self.form_layout.addRow(QLabel("Description:"), self.desc_edit)
        self.form_layout.addRow(QLabel("Category:"), self.cat_edit)
        self.form_layout.addRow(QLabel("Amount:"), self.amount_edit)

        self.layout.addLayout(self.form_layout)

    def _create_buttons(self):
        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Expense")
        self.add_button.clicked.connect(self.add_expense)

        self.update_button = QPushButton("Update Selected")
        self.update_button.clicked.connect(self.update_expense)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_expense)

        self.summary_button = QPushButton("Show Summary")
        self.summary_button.clicked.connect(self.show_summary)

        self.clear_button = QPushButton("Clear Form")
        self.clear_button.clicked.connect(self.clear_form)

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.update_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.summary_button)
        self.button_layout.addWidget(self.clear_button)

        self.layout.addLayout(self.button_layout)

    def populate_table(self, expenses):
        """Clears the table and fills it with a given list of expenses."""
        self.table.setRowCount(0)
        for row_num, expense in enumerate(expenses):
            self.table.insertRow(row_num)
            for col_num, field in enumerate(FIELDNAMES):
                item = QTableWidgetItem(expense.get(field, ""))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_num, col_num, item)
        self.clear_form()

    def load_expenses(self):
        """Loads all expenses from the CSV and populates the table."""
        all_expenses = get_expenses()
        self.populate_table(all_expenses)

    def populate_form_from_selection(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row_index = selected_rows[0].row()
        try:
            date = QDate.fromString(self.table.item(row_index, 0).text(), "yyyy-MM-dd")
            self.date_edit.setDate(date)
            self.desc_edit.setText(self.table.item(row_index, 1).text())
            self.cat_edit.setText(self.table.item(row_index, 2).text())
            self.amount_edit.setText(self.table.item(row_index, 3).text())
        except Exception as e:
            print(f"Error populating form: {e}")  # For debugging
            self.clear_form()

    def add_expense(self):
        date = self.date_edit.date().toString("yyyy-MM-dd")
        description = self.desc_edit.text().strip()
        category = self.cat_edit.text().strip()
        amount_str = self.amount_edit.text().strip()

        if not all([description, category, amount_str]):
            QMessageBox.warning(self, "Input Error", "All fields must be filled out.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a valid number.")
            return

        new_expense = {'Date': date, 'Description': description, 'Category': category, 'Amount': f"{amount:.2f}"}

        expenses = get_expenses()
        expenses.append(new_expense)
        save_all_expenses(expenses)
        self.load_expenses()

    def update_expense(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an expense to update.")
            return

        row_index = selected_rows[0].row()

        # Get updated data from the form
        date = self.date_edit.date().toString("yyyy-MM-dd")
        description = self.desc_edit.text().strip()
        category = self.cat_edit.text().strip()
        amount_str = self.amount_edit.text().strip()

        if not all([description, category, amount_str]):
            QMessageBox.warning(self, "Input Error", "All fields must be filled out.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a valid number.")
            return

        updated_expense = {'Date': date, 'Description': description, 'Category': category, 'Amount': f"{amount:.2f}"}

        expenses = get_expenses()
        expenses[row_index] = updated_expense
        save_all_expenses(expenses)
        self.load_expenses()

    def delete_expense(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an expense to delete.")
            return

        row_index = selected_rows[0].row()

        reply = QMessageBox.question(self, "Confirm Deletion",
                                     "Are you sure you want to delete this expense?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            expenses = get_expenses()
            expenses.pop(row_index)
            save_all_expenses(expenses)
            self.load_expenses()

    def _create_search_bar(self):
        """Creates the search input fields and buttons."""
        search_layout = QHBoxLayout()

        self.search_keyword_edit = QLineEdit()
        self.search_keyword_edit.setPlaceholderText("Search by keyword...")

        self.search_category_edit = QLineEdit()
        self.search_category_edit.setPlaceholderText("Filter by category...")

        self.search_date_edit = QLineEdit()
        self.search_date_edit.setPlaceholderText("Filter by date (YYYY-MM-DD)...")

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)

        self.clear_search_button = QPushButton("Clear Search")
        self.clear_search_button.clicked.connect(self.clear_search)

        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_keyword_edit)
        search_layout.addWidget(self.search_category_edit)
        search_layout.addWidget(self.search_date_edit)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_search_button)

        # Add this new layout to the main vertical layout
        self.layout.addLayout(search_layout)

    def perform_search(self):
        """Executes the search and updates the table with results."""
        keyword = self.search_keyword_edit.text().strip()
        category = self.search_category_edit.text().strip()
        date_str = self.search_date_edit.text().strip()

        # Use the backend function to get filtered results
        filtered_expenses = search_expenses(keyword, category, date_str)

        # Populate the table with only the filtered results
        self.populate_table(filtered_expenses)

    def clear_search(self):
        """Clears search fields and reloads all expenses."""
        self.search_keyword_edit.clear()
        self.search_category_edit.clear()
        self.search_date_edit.clear()
        self.load_expenses()  # Reloads the full list

    def show_summary(self):
        summary_text = get_summary_text()
        QMessageBox.information(self, "Expense Summary", summary_text)

    def clear_form(self):
        self.date_edit.setDate(QDate.currentDate())
        self.desc_edit.clear()
        self.cat_edit.clear()
        self.amount_edit.clear()
        self.table.clearSelection()
