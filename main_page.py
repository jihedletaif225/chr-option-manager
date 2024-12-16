from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMainWindow
from add_group_to_product import Add_Group_to_ProductGUI
from option_uploader import OptionsUploaderGUI
from add_options_to_group import RestoConcept_Option_ManagerGUI



class MainPage(QWidget):
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self.setWindowTitle("Main Page")
        self.setGeometry(100, 100, 600, 600)

        # Layout for the main page
        main_layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel("Welcome to the Main Page!")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498db; margin-bottom: 20px;")
        main_layout.addWidget(title_label)

        # Navigation buttons
        self.options_uploader_button = QPushButton("Go to Options Uploader")
        self.options_uploader_button.clicked.connect(self.open_options_uploader)
        main_layout.addWidget(self.options_uploader_button)

        self.option_manager_button = QPushButton("Go to Option Manager")
        self.option_manager_button.clicked.connect(self.open_option_manager)
        main_layout.addWidget(self.option_manager_button)

        self.add_group_button = QPushButton("Go to Add Group to Product")
        self.add_group_button.clicked.connect(self.open_add_group)
        main_layout.addWidget(self.add_group_button)

    def open_options_uploader(self):
        self.options_uploader_page = OptionsUploaderGUI(self.username, self.password)
        self.options_uploader_page.show()

    def open_option_manager(self):
        self.option_manager_page = RestoConcept_Option_ManagerGUI(self.username, self.password)
        self.option_manager_page.show()

    def open_add_group(self):
        self.add_group_page = Add_Group_to_ProductGUI(self.username, self.password)
        self.add_group_page.show()

