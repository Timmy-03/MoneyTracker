import sys
from PyQt6.QtWidgets import QApplication

# --- Import the GUI class and the initialization function ---
from GUI import ExpenseTrackerApp
from Code_Function import initialize_csv

# --- Application Entry Point ---
if __name__ == "__main__":
    # Ensure the CSV file exists before starting the app
    initialize_csv()

    # Create the application object
    app = QApplication(sys.argv)

    # Create an instance of our main window
    main_window = ExpenseTrackerApp()

    # Show the window
    main_window.show()

    # Start the application's event loop
    sys.exit(app.exec())