import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import QDate
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
    QTableWidgetItem
)

class ExpenseApp(QWidget):
    def __init__(self):
        super().__init__()
        # Main App Objects and Settings
        self.resize(1100, 1000)
        self.setWindowTitle("SHANZ Expenses")

        self.date_box = QDateEdit()
        self.dropdown = QComboBox()
        self.amount = QLineEdit()
        self.description = QLineEdit()

        self.add_button = QPushButton("Add Expenses")
        self.delete_button = QPushButton("Delete Expenses")
        self.add_button.clicked.connect(self.add_expenses)
        self.delete_button.clicked.connect(self.delete_expenses)

        self.table = QTableWidget()
        self.table.setColumnCount(5) # Id, Date, Category, Amount, Description
        header_names = ["Id", "Date", "Category", "Amount", "Description"]
        self.table.setHorizontalHeaderLabels(header_names)

        # Design App with Layouts
        self.dropdown.addItems([
            "Food",
            "Transportation",
            "Rent",
            "Shopping",
            "entertainment",
            "Bills",
            "Other"])

        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        self.row3 = QHBoxLayout()

        self.row1.addWidget(QLabel("Date:"))
        self.row1.addWidget(self.date_box)
        self.row1.addWidget(QLabel("Categories:"))
        self.row1.addWidget(self.dropdown)

        self.row2.addWidget(QLabel("Amount:"))
        self.row2.addWidget(self.amount)
        self.row2.addWidget(QLabel("Description:"))
        self.row2.addWidget(self.description)

        self.row3.addWidget(self.add_button)
        self.row3.addWidget(self.delete_button)

        self.master_layout.addLayout(self.row1)
        self.master_layout.addLayout(self.row2)
        self.master_layout.addLayout(self.row3)

        self.master_layout.addWidget(self.table)

        self.setLayout(self.master_layout)

        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)

        query = QSqlQuery("SELECT * FROM expenses")
        row = 0
        while query.next():
            expense_id = query.value(0)
            date = query.value(1)
            category = query.value(2)
            amount = query.value(3)
            description = query.value(4)

            # Add the values in the database into the visual table
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(expense_id)))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(category))
            self.table.setItem(row, 3, QTableWidgetItem(str(amount)))
            self.table.setItem(row, 4, QTableWidgetItem(description))
            row += 1

    def add_expenses(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        category = self.dropdown.currentText()
        amount = self.amount.text()
        description = self.description.text()

        query = QSqlQuery()
        query.prepare("""
            INSERT INTO expenses (date, category, amount, description)
            VALUES (?, ?, ?, ?)
        """)
        query.addBindValue(date)
        query.addBindValue(category)
        query.addBindValue(amount)
        query.addBindValue(description)
        query.exec_()

        self.date_box.setDate(QDate.currentDate())
        self.dropdown.setCurrentIndex(0)
        self.amount.clear()
        self.description.clear()

        self.load_table()

    def delete_expenses(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Expenses Chosen", "Please choose an expense to delete!")
            return

        expense_id = int(self.table.item(selected_row, 0).text())

        confirm = QMessageBox.question("Are you sure?", "Delete Expense?", QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return

        query = QSqlQuery()
        query.prepare("DELETE FROM expenses WHERE id = ?")
        query.addBindValue(expense_id)
        query.exec_()

        self.load_table()

# Create Databases
database = QSqlDatabase.addDatabase("QSQLITE")
database.setDatabaseName("expense.db")

if not database.open():
    QMessageBox.critical(None, "Error", "Could not open your Database")
    sys.exit(1)

query = QSqlQuery()
query.exec_("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
""")

# Run the App
if __name__ == '__main__':
    app = QApplication([])
    main = ExpenseApp()
    main.show()
    app.exec_()

