

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QCheckBox, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from main_page import MainPage

class LoginWorker(QThread):

    login_successful = pyqtSignal(bool)
    log_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, username, password, headless=True):
        super().__init__()
        self.username = username
        self.password = password
        self.headless = headless
        self.login_success = False

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            try:
                self.login(page)
                self.login_success = True
                self.login_successful.emit(True)  # Emit success signal on successful login
            except Exception as e:
                self.log_update.emit(f"An error occurred: {str(e)}")
                self.login_successful.emit(False)
            finally:
                browser.close()
                self.finished.emit()

    def login(self, page):
        self.log_update.emit("Attempting to log in...")
        self.progress_update.emit(10)
        page.goto("https://www.restoconcept.com/admin/logon.asp")
        page.fill("#adminuser", self.username)
        page.fill("#adminPass", self.password)
        page.click("#btn1")
        try:
            page.wait_for_selector(
                'td[align="center"][style="background-color:#eeeeee"]:has-text("© Copyright 2024 - Restoconcept")',
                timeout=5000
            )
            self.log_update.emit("Login successful.")
            self.progress_update.emit(100)
        except PlaywrightTimeoutError:
            raise Exception("Login failed. Please check your username and password.")
        



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Product Group Automation")
        self.setGeometry(100, 100, 600, 600)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Title
        self.title_label = QLabel("Login")
        self.title_label.setObjectName("titleLabel")
        main_layout.addWidget(self.title_label)

        # Frame for input fields
        input_frame = QFrame()
        input_layout = QVBoxLayout()
        input_frame.setLayout(input_layout)
        main_layout.addWidget(input_frame)

        # Input fields
        self.username_input = self.create_input_field("Username ", input_layout)
        self.password_input = self.create_input_field("Password ", input_layout, is_password=True)

        # Headless mode checkbox
        self.headless_checkbox = QCheckBox("Run in headless mode")
        self.headless_checkbox.setChecked(True)
        input_layout.addWidget(self.headless_checkbox)

        # Start button
        self.start_button = QPushButton("Login")
        self.start_button.clicked.connect(self.start_login)
        input_layout.addWidget(self.start_button)

        # # Progress bar
        # self.progress_bar = QProgressBar()
        # main_layout.addWidget(self.progress_bar)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)

    def create_input_field(self, label_text, layout, is_password=False):
        label = QLabel(label_text)
        input_field = QLineEdit()
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field

    def start_login(self):
        # Collect the necessary parameters for login
        username = self.username_input.text()
        password = self.password_input.text()
        headless = self.headless_checkbox.isChecked()

        # Create the LoginWorker thread with the collected parameters
        self.login_worker = LoginWorker(username, password, headless)

        # Connect signals for logging, progress updates, and when the process finishes
        self.login_worker.log_update.connect(self.log_message)
        # self.login_worker.progress_update.connect(self.update_progress_bar)
        self.login_worker.login_successful.connect(self.handle_login_result)
        self.login_worker.finished.connect(self.on_login_finished)

        # Start the login thread
        self.login_worker.start()

    def log_message(self, message):
        # Method to update the log display
        self.log_output.append(message)

    # def update_progress_bar(self, value):
    #     # Method to update the progress bar
    #     self.progress_bar.setValue(value)

    def handle_login_result(self, success):
        self.login_success = success

    def on_login_finished(self):

        # If login was successful
        if getattr(self, 'login_success', False):
        # Check for the signal 
            self.log_message("Login successful.")
            # self.progress_bar.setValue(100)
        
        # Hide the login window and show the main page
            self.hide()  # Hide login window
            self.main_page = MainPage(
                self.username_input.text(),
                self.password_input.text())  # Pass username and password
        # Create main page
            self.main_page.show()  # Show main page
        else:
        # If login failed, display an error message
            self.log_message("Login failed. Please check your username and password.")


    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f6f6f6;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                color: #333333;
            }
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            }
            QLabel {
                font-size: 13px;
                line-height: 19px;
                color: #111;
                font-family: "Amazon Ember", Arial, sans-serif;
                padding-left: 2px;
                padding-bottom: 2px;
                font-weight: 500;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 8px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #3498db;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 8px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 8px;
            }
            QTextEdit {
                background-color: #f6f6f6;
            }
        """)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498db; margin-bottom: 20px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())