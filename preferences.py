from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

import configparser

class EditPreferences(QWidget):
    def __init__(self):
        super(EditPreferences, self).__init__()
        self.setWindowFlags(Qt.SubWindow)
        self.setWindowTitle("Settings")

        self.apikey_label = QLabel("API Key:")
        self.backend_label = QLabel("后端地址:")
        self.apikey_line = QLineEdit()
        self.apikey_line.setFixedWidth(400)
        self.backend_line = QLineEdit()
        self.backend_line.setFixedWidth(400)
        
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.apikey_line.setText(self.config.get('zhipuai', 'api_key'))
        self.backend_line.setText(self.config.get('backend', 'base_url'))

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.close)
        self.btn_save = QPushButton("保存")
        self.btn_save.clicked.connect(self.save)

        self.v_layout = QVBoxLayout()
        self.g_layout1 = QGridLayout()
        self.g_layout1.addWidget(self.apikey_label, 0, 0)
        self.g_layout1.addWidget(self.apikey_line, 0, 1)
        self.g_layout1.addWidget(self.backend_label, 1, 0)
        self.g_layout1.addWidget(self.backend_line, 1, 1)
        self.g_layout2 = QGridLayout()
        self.g_layout2.addWidget(self.btn_cancel, 0, 0)
        self.g_layout2.addWidget(self.btn_save, 0, 2)
        self.v_layout.addLayout(self.g_layout1)
        self.v_layout.addLayout(self.g_layout2)
        self.setLayout(self.v_layout)

    def save(self):
        # Save settings
        self.config.set('zhipuai', 'api_key', self.apikey_line.text())
        self.config.set('backend', 'base_url', self.backend_line.text())
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

        self.close()
