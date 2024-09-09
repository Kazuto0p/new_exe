import sys
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QGridLayout, QInputDialog, QMessageBox, QLineEdit, QComboBox, QDialog, QFormLayout
)
import psutil
from close import close_application_by_path, close_application_by_name

# Initialize services as an empty dictionary
services = {}

class AddEditServiceDialog(QDialog):
    def __init__(self, parent=None, entry_key=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Service/Application")
        self.entry_key = entry_key
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        # Display Name
        self.display_name_input = QLineEdit(self)
        layout.addRow("Display Name:", self.display_name_input)

        # Command/Service Name
        self.command_input = QLineEdit(self)
        layout.addRow("Service/Application Name or Path:", self.command_input)

        # Type Dropdown
        self.type_input = QComboBox(self)
        self.type_input.addItems(["Service", "Application"])
        layout.addRow("Type:", self.type_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addRow(button_layout)
        self.setLayout(layout)

        # If editing, populate fields
        if self.entry_key:
            entry = services[self.entry_key]
            self.display_name_input.setText(entry['display_name'])
            self.command_input.setText(entry['command'])
            self.type_input.setCurrentText(entry['type'])

    def get_data(self):
        return {
            'display_name': self.display_name_input.text().strip(),
            'command': self.command_input.text().strip(),
            'type': self.type_input.currentText()
        }

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Service/Application Manager")
        self.setGeometry(100, 100, 600, 400)

        # Initialize UI
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)

        # Button layout for adding and editing services
        button_layout = QHBoxLayout()

        # Add New Service/Application button
        self.add_service_button = QPushButton("+ New", self)
        self.add_service_button.clicked.connect(self.add_new_service)
        button_layout.addWidget(self.add_service_button)

        # Edit Service/Application button
        self.edit_service_button = QPushButton("Edit", self)
        self.edit_service_button.clicked.connect(self.edit_service)
        button_layout.addWidget(self.edit_service_button)

        # Delete Service/Application button
        self.delete_service_button = QPushButton("Delete", self)
        self.delete_service_button.clicked.connect(self.delete_service)
        button_layout.addWidget(self.delete_service_button)

        self.main_layout.addLayout(button_layout)

        # Grid layout for services/applications and corresponding buttons
        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)

        # Populate the grid with services/applications and their corresponding buttons
        self.populate_services()

    def populate_services(self):
        """Clear the layout and add service/application names and their corresponding buttons."""
        # Clear the grid layout first
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.service_buttons = {}
        for i, entry_key in enumerate(services):
            entry = services[entry_key]

            # Service/Application label
            service_label = QLabel(entry['display_name'])
            self.grid_layout.addWidget(service_label, i, 0)

            # Start button
            start_button = QPushButton("Start")
            start_button.clicked.connect(lambda _, key=entry_key: self.start_service(key))
            self.grid_layout.addWidget(start_button, i, 1)

            # Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(lambda _, key=entry_key: self.close_service(key))
            self.grid_layout.addWidget(close_button, i, 2)

            # Save buttons for future reference
            self.service_buttons[entry_key] = start_button

    def start_service(self, entry_key):
        """Handle starting of a service/application."""
        entry = services[entry_key]
        try:
            if entry['type'] == "Application":
                subprocess.Popen(entry['command'], shell=True)
                QMessageBox.information(self, "Success", f"'{entry['display_name']}' started successfully.", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Info", "Service start functionality is not implemented.", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start '{entry['display_name']}'.\nError: {e}", QMessageBox.Ok)

    def close_service(self, entry_key):
        """Handle closing of a service/application."""
        entry = services[entry_key]
        try:
            if entry['type'] == "Application":
                if close_application_by_path(entry['command']) or close_application_by_name(entry['display_name']):
                    QMessageBox.information(self, "Success", f"'{entry['display_name']}' closed successfully.", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Error", f"Failed to close '{entry['display_name']}'.", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Info", "Service close functionality is not implemented.", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to close '{entry['display_name']}'.\nError: {e}", QMessageBox.Ok)

    def add_new_service(self):
        """Handle the addition of a new service/application."""
        dialog = AddEditServiceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['display_name'] and data['command']:
                services[data['display_name']] = data
                self.populate_services()
                QMessageBox.information(self, "Success", "New entry added successfully.", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Input Error", "Please provide valid inputs for all fields.", QMessageBox.Ok)

    def edit_service(self):
        """Handle editing of an existing service/application."""
        if not services:
            QMessageBox.warning(self, "Error", "No services/applications available to edit.", QMessageBox.Ok)
            return

        entry_key, ok = QInputDialog.getItem(self, "Edit Service/Application", "Select the service/application to edit:", list(services.keys()), 0, False)
        if ok and entry_key:
            dialog = AddEditServiceDialog(self, entry_key)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if data['display_name'] and data['command']:
                    services[data['display_name']] = data
                    if entry_key != data['display_name']:
                        del services[entry_key]
                    self.populate_services()
                    QMessageBox.information(self, "Success", "Entry updated successfully.", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Input Error", "Please provide valid inputs for all fields.", QMessageBox.Ok)

    def delete_service(self):
        """Handle the deletion of a service/application."""
        if not services:
            QMessageBox.warning(self, "Error", "No services/applications available to delete.", QMessageBox.Ok)
            return

        entry_key, ok = QInputDialog.getItem(self, "Delete Service/Application", "Select the service/application to delete:", list(services.keys()), 0, False)
        if ok and entry_key:
            confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete '{entry_key}'?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                del services[entry_key]
                self.populate_services()
                QMessageBox.information(self, "Success", "Entry deleted successfully.", QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MyApp()
    mainWin.show()
    sys.exit(app.exec_())
