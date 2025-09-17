from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QDateEdit,
    QLabel, QHeaderView, QMessageBox, QFormLayout, QComboBox
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import QDate, Qt

# --- Import updated backend functions and constants ---
from Code_Function import (
    get_transactions, save_all_transactions, get_summary_text, FIELDNAMES,
    search_transactions, sort_transactions_by_date
)


class ExpenseTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Finance Tracker")
        self.setGeometry(100, 100, 800, 600)

        self.current_transactions = []
        self.sort_order = Qt.SortOrder.AscendingOrder

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self._create_search_bar()
        self._create_table()
        self._create_input_form()
        self._create_buttons()

        self.table.itemSelectionChanged.connect(self.populate_form_from_selection)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

        self.load_transactions()

    def _refresh_table_data(self, transactions_list):
        """
        A central method to sort and display any list of transactions.
        This ensures the table is always sorted correctly.
        """
        # 1. Sort the provided list according to the current sort order
        descending = (self.sort_order == Qt.SortOrder.DescendingOrder)
        self.current_transactions = sort_transactions_by_date(transactions_list, descending=descending)

        # 2. Populate the table with the now-sorted data
        self.populate_table(self.current_transactions)

        # 3. Visually update the header's sort indicator arrow
        # We know the date column is always at index 0
        self.table.horizontalHeader().setSortIndicator(0, self.sort_order)

    def _create_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(FIELDNAMES))
        self.table.setHorizontalHeaderLabels(FIELDNAMES)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layout.addWidget(self.table)

    def _create_input_form(self):
        self.form_layout = QFormLayout()

        # --- NEW: Type selector dropdown ---
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Expense", "Income"])

        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.desc_edit = QLineEdit()
        self.cat_edit = QLineEdit()
        self.amount_edit = QLineEdit()

        self.form_layout.addRow(QLabel("Type:"), self.type_combo)  # <-- Add to form
        self.form_layout.addRow(QLabel("Date:"), self.date_edit)
        self.form_layout.addRow(QLabel("Description:"), self.desc_edit)
        self.form_layout.addRow(QLabel("Category:"), self.cat_edit)
        self.form_layout.addRow(QLabel("Amount:"), self.amount_edit)
        self.layout.addLayout(self.form_layout)

    def _create_buttons(self):
        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)

        self.update_button = QPushButton("Update Selected")
        self.update_button.clicked.connect(self.update_transaction)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_transaction)

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

    def populate_table(self, transactions):
        self.table.setRowCount(0)
        for row_num, transaction in enumerate(transactions):
            self.table.insertRow(row_num)
            for col_num, field in enumerate(FIELDNAMES):
                item = QTableWidgetItem(transaction.get(field, ""))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # --- NEW: Color coding block ---
                if field == 'Amount':
                    trans_type = transaction.get('Type', 'Expense')
                    if trans_type == 'Income':
                        item.setBackground(QColor(220, 255, 220))  # Light green background
                        item.setForeground(QColor(0, 0, 0))  # Set text to black
                    else:  # Expense
                        item.setBackground(QColor(255, 220, 220))  # Light red background
                        item.setForeground(QColor(0, 0, 0))  # Set text to black

                self.table.setItem(row_num, col_num, item)
        self.clear_form()

    def load_transactions(self):
        all_transactions = get_transactions()
        self._refresh_table_data(all_transactions)

    def populate_form_from_selection(self):
        # ... (logic is the same, but now populates the type combo box) ...
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        row_index = selected_rows[0].row()
        try:
            # Set the type in the dropdown
            trans_type = self.table.item(row_index, 1).text()
            self.type_combo.setCurrentText(trans_type)

            date = QDate.fromString(self.table.item(row_index, 0).text(), "yyyy-MM-dd")
            self.date_edit.setDate(date)
            self.desc_edit.setText(self.table.item(row_index, 2).text())
            self.cat_edit.setText(self.table.item(row_index, 3).text())
            self.amount_edit.setText(self.table.item(row_index, 4).text())
        except Exception as e:
            print(f"Error populating form: {e}")
            self.clear_form()

    def add_transaction(self): # Renamed
        trans_type = self.type_combo.currentText() # Get type from dropdown
        date = self.date_edit.date().toString("yyyy-MM-dd")
        description = self.desc_edit.text().strip()
        category = self.cat_edit.text().strip()
        amount_str = self.amount_edit.text().strip()


        if not all([description, category, amount_str]):
            QMessageBox.warning(self, "Input Error", "All fields must be filled out.")
            return

        try:
            amount_str = float(amount_str)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a valid number.")
            return

        new_transaction = {
            'Date': date, 'Type': trans_type, 'Description': description,
            'Category': category, 'Amount': f"{float(amount_str):.2f}"
        }

        transactions = get_transactions()
        transactions.append(new_transaction)
        save_all_transactions(transactions)
        self.load_transactions()

    def update_transaction(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an transaction to update.")
            return

        row_index = selected_rows[0].row()

        # Get updated data from the form
        trans_type = self.type_combo.currentText()
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

        updated_transaction = {
            'Date': date, 'Type': trans_type, 'Description': description,
            'Category': category, 'Amount': f"{amount:.2f}"
        }

        transaction = get_transactions()
        transaction[row_index] = updated_transaction
        save_all_transactions(transaction)
        self.load_transactions()

    def delete_transaction(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an transaction to delete.")
            return

        row_index = selected_rows[0].row()

        reply = QMessageBox.question(self, "Confirm Deletion",
                                     "Are you sure you want to delete this transaction?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            transactions = get_transactions()
            transactions.pop(row_index)  # Use pop() to remove the item
            save_all_transactions(transactions)
            self.load_transactions()

    def _create_search_bar(self):
        """Creates the search input fields and buttons."""
        search_layout = QHBoxLayout()

        self.search_keyword_edit = QLineEdit()
        self.search_keyword_edit.setPlaceholderText("Keyword for description...")

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

        # --- ERROR HANDLING BLOCK ---
        # Check if all search fields are empty after stripping whitespace.
        if not keyword and not category and not date_str:
            QMessageBox.warning(self, "Empty Search", "Please enter at least one search term to perform a search.")
            return  # Stop the function here if the search is empty

        filtered_transactions = search_transactions(keyword, category, date_str)
        self._refresh_table_data(filtered_transactions)

    def clear_search(self):
        """Clears search fields and reloads all expenses."""
        self.search_keyword_edit.clear()
        self.search_category_edit.clear()
        self.search_date_edit.clear()
        self.load_transactions()  # Reloads the full list

    def on_header_clicked(self, logicalIndex):
        """Handles clicks on the table header to sort columns."""
        # We only want to sort the 'Date' column, which is at index 0
        if logicalIndex == 0:
            # Toggle the sort order
            if self.sort_order == Qt.SortOrder.AscendingOrder:
                self.sort_order = Qt.SortOrder.DescendingOrder
            else:
                self.sort_order = Qt.SortOrder.AscendingOrder

            # Re-sort and refresh the *currently visible* data
            self._refresh_table_data(self.current_transactions)

            # Update the table with the sorted data
            self.populate_table(self.current_transactions)

    def show_summary(self):
        summary_text = get_summary_text()

        # Create a monospaced font for perfect alignment
        mono_font = QFont()
        mono_font.setFamily("Courier New")
        mono_font.setPointSize(10)

        # Create the message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Transaction Summary")
        msg_box.setText(summary_text)
        msg_box.setIcon(QMessageBox.Icon.Information)

        # Apply the font
        msg_box.setFont(mono_font)

        # Show the message box
        msg_box.exec()

    def clear_form(self):
        self.date_edit.setDate(QDate.currentDate())
        self.desc_edit.clear()
        self.cat_edit.clear()
        self.amount_edit.clear()
        self.table.clearSelection()