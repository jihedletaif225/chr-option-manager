

import sys
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QFileDialog, QProgressBar, QCheckBox, QFrame, QMessageBox, QTextEdit)
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from login_handler import LoginManager
from config import BASE_URL


class OptionsUploaderThread(QThread):
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    log_update = pyqtSignal(str)

    def __init__(self, excel_file, username, password, headless):
        super().__init__()
        self.excel_file = excel_file
        self.username = username
        self.password = password
        self.headless = headless

    def run(self):
        try:
            options_df = pd.read_excel(self.excel_file)
            total_rows = len(options_df)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context()
                page = context.new_page()

                self.log_update.emit("Starting the upload process...")
                login_manager = LoginManager(self.username, self.password)
                if not login_manager.login(page):
                    self.error_occurred.emit("Login failed. Please check your username and password.")
                    return 

                for index, row in options_df.iterrows():
                    self.status_update.emit(f"Processing option {index + 1} of {total_rows}")
                    self.log_update.emit(f"Processing option {index + 1} of {total_rows}")

                    try:
                        self.navigate_to_options_page(page)
                        self.fill_option_form(page, row)
                        self.submit_option(page)
                        self.handle_submission_result(page)
                    except Exception as e:
                        self.log_update.emit(f"Error processing option {index + 1}: {str(e)}")
                        continue

                    progress = int((index + 1) / total_rows * 100)
                    self.progress_update.emit(progress)

        except Exception as e:
            self.error_occurred.emit(f"An error occurred: {str(e)}")
            self.log_update.emit(f"Critical error: {str(e)}")

        self.status_update.emit("Upload process completed.")
        self.log_update.emit("Upload process completed. Check the log for details.")

    
    def navigate_to_options_page(self, page):
        page.goto(f"{BASE_URL}/options/optionslist.asp")
        page.click('a[href="/admin/SA_opt_edit.asp?action=add"]')

    def fill_option_form(self, page, row):
        optionDescrip = str(row['optionDescrip']) if pd.notna(row['optionDescrip']) else ''
        ref = str(row['ref']) if pd.notna(row['ref']) else ''
        pricetoadd = str(row['pricetoadd']) if pd.notna(row['pricetoadd']) else ''
        prixpublic = str(row['prixpublic']) if pd.notna(row['prixpublic']) else ''
        iddelai = str(row['iddelai']) if pd.notna(row['iddelai']) else ''

        page.fill("#optionDescrip", optionDescrip)
        page.fill("#ref", ref)
        page.fill("#pricetoadd", pricetoadd)
        page.fill("#prixpublic", prixpublic)
        page.select_option("#iddelai", iddelai)

    def submit_option(self, page):
        page.click('button:has-text("Ajouter")')
        page.wait_for_load_state("networkidle")

    def handle_submission_result(self, page):
        if page.query_selector('text="Option déjà créée"'):
            self.log_update.emit("Option already exists. Skipping...")
        elif page.query_selector('text="Session expirée"'):
            self.log_update.emit("Session expired. Logging in again...")
            self.login(page)
        elif page.query_selector('text="Option ajoutée avec succès"'):
            self.log_update.emit("Option added successfully.")
        else:
            self.log_update.emit("Unexpected result after submission. Check manually.")

class OptionsUploaderGUI(QWidget):
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self.initUI()
        self.apply_styles()

    def initUI(self):
        self.setWindowTitle('RestoConcept Options Uploader')
        self.setGeometry(100, 100, 600, 600)

        layout = QVBoxLayout()

        self.file_label = QLabel("Select Excel File:")
        layout.addWidget(self.file_label)
        
        file_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_button = QPushButton("Browse")
        self.file_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.file_button)
        layout.addLayout(file_layout)

        self.headless_checkbox = QCheckBox("Run in headless mode")
        self.headless_checkbox.setChecked(True)
        layout.addWidget(self.headless_checkbox)

        self.upload_button = QPushButton("Upload Options")
        self.upload_button.clicked.connect(self.start_upload)
        layout.addWidget(self.upload_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.log_textarea = QTextEdit()
        self.log_textarea.setReadOnly(True)
        layout.addWidget(self.log_textarea)

        self.setLayout(layout)

    def apply_styles(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
        QApplication.setPalette(palette)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")
        if file_path:
            self.file_input.setText(file_path)

    def start_upload(self):
        excel_file = self.file_input.text()
        headless = self.headless_checkbox.isChecked()

        if not excel_file:
            QMessageBox.warning(self, "Input Error", "Please select an Excel file.")
            return

        self.thread = OptionsUploaderThread(excel_file, self.username, self.password, headless)
        self.thread.progress_update.connect(self.progress_bar.setValue)
        self.thread.status_update.connect(self.status_label.setText)
        self.thread.log_update.connect(self.log_textarea.append)
        self.thread.error_occurred.connect(self.handle_error)
        self.thread.start()

    def handle_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Example usage: Pass username and password when initializing the GUI
    gui = OptionsUploaderGUI("example_user", "example_pass")
    gui.show()
    sys.exit(app.exec_())
