import os
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QComboBox,
    QLineEdit,
    QDateEdit,
    QTableWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QTableWidgetItem,
    QFrame,
    QAbstractItemView,
    QHeaderView
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor, QPalette

# Fix for high-DPI scaling
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
os.environ["QT_ENABLE_HIDPI_SCALING"] = "1"

STYLE_PATH = "/home/salimhabeshawi/SHANZexpenses/style.css"

def load_stylesheet():
    if os.path.exists(STYLE_PATH):
        with open(STYLE_PATH, "r") as f:
            return f.read()
    return ""

class ExpenseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_db()
        self.setup_ui()
        self.load_table()

    def init_db(self):
        self.conn = sqlite3.connect("expense.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                amount REAL,
                description TEXT
            )
        """)
        self.conn.commit()

    def setup_ui(self):
        self.resize(1100, 700)
        self.setWindowTitle("SHANZ Expenses")
        
        # New central main layout (no sidebar)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Container Box (The main bordered frame)
        self.container = QFrame()
        self.container.setObjectName("main_container")
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # --- Left Pane (Now contains the Table) ---
        self.left_pane = QFrame()
        self.left_pane.setObjectName("left_pane")
        left_layout = QVBoxLayout(self.left_pane)
        left_layout.setContentsMargins(30, 30, 30, 30)
        left_layout.setSpacing(20)
        
        title = QLabel("Transaction History")
        title.setObjectName("form_title")
        left_layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Category", "Amount", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        left_layout.addWidget(self.table)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setObjectName("delete_btn")
        self.delete_button.clicked.connect(self.delete_expenses)
        left_layout.addWidget(self.delete_button, alignment=Qt.AlignRight)
        
        container_layout.addWidget(self.left_pane, 7) # Table side takes more space
        
        # --- Right Pane (Input Form) ---
        self.right_pane = QFrame()
        self.right_pane.setObjectName("right_pane")
        right_layout = QVBoxLayout(self.right_pane)
        right_layout.setContentsMargins(50, 50, 50, 50)
        right_layout.setSpacing(15)
        
        form_title = QLabel("Log an Expense")
        form_title.setObjectName("form_title")
        right_layout.addWidget(form_title)
        
        form_desc = QLabel("Enter record details below")
        form_desc.setObjectName("form_desc")
        right_layout.addWidget(form_desc)
        
        # Form Fields
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())
        self.date_box.setCalendarPopup(True)
        
        self.dropdown = QComboBox()
        self.dropdown.addItems(["Food", "Transport", "Rent", "Shopping", "Entertainment", "Bills", "Other"])
        
        self.amount = QLineEdit()
        self.amount.setPlaceholderText("Amount ($)")
        
        self.description = QLineEdit()
        self.description.setPlaceholderText("Description")
        
        right_layout.addWidget(QLabel("Date:"))
        right_layout.addWidget(self.date_box)
        right_layout.addWidget(QLabel("Category:"))
        right_layout.addWidget(self.dropdown)
        right_layout.addWidget(QLabel("Amount:"))
        right_layout.addWidget(self.amount)
        right_layout.addWidget(QLabel("Description:"))
        right_layout.addWidget(self.description)
        
        self.add_button = QPushButton("Add Expense")
        self.add_button.setObjectName("continue_btn")
        self.add_button.clicked.connect(self.add_expenses)
        right_layout.addWidget(self.add_button)
        
        self.sum_label = QLabel("Total: $0.00")
        self.sum_label.setObjectName("sum_label")
        self.sum_label.setAlignment(Qt.AlignRight)
        right_layout.addWidget(self.sum_label)
        
        container_layout.addWidget(self.right_pane, 3) # Form side
        
        self.main_layout.addWidget(self.container)

    def load_table(self):
        self.table.setRowCount(0)
        self.cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        rows = self.cursor.fetchall()
        total_amount = 0.0
        for row_idx, row_data in enumerate(rows):
            date = row_data[1]
            category = row_data[2]
            amount = row_data[3]
            description = row_data[4]

            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(date)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(category)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"${float(amount):.2f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(description)))
            
            try:
                total_amount += float(amount)
            except: pass

        self.sum_label.setText(f"Total Expenses: ${total_amount:.2f}")

    def add_expenses(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        category = self.dropdown.currentText()
        amount = self.amount.text()
        description = self.description.text()

        if not amount:
            QMessageBox.warning(self, "Error", "Please enter an amount.")
            return

        try:
            val = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid amount.")
            return

        self.cursor.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)", 
                           (date, category, val, description))
        self.conn.commit()

        self.amount.clear()
        self.description.clear()
        self.load_table()
        
        QMessageBox.information(self, "Success", "Expense added successfully!")

    def delete_expenses(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Expenses Chosen", "Please choose an expense to delete!")
            return

        date = self.table.item(selected_row, 0).text()
        amount_str = self.table.item(selected_row, 2).text().replace("$", "")
        
        confirm = QMessageBox.question(self, "Are you sure?", "Delete Expense?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No: return

        self.cursor.execute("DELETE FROM expenses WHERE date = ? AND amount = ?", (date, float(amount_str)))
        self.conn.commit()

        self.load_table()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#F4EBD9"))
    app.setPalette(palette)
    
    window = ExpenseApp()
    window.show()
    sys.exit(app.exec_())
