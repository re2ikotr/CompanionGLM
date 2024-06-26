import os
import sys
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import *
from handyllm import PromptConverter

file_name = "paimon5.txt"
dir_name = "prompts"
converter = PromptConverter()
file_path = os.path.join(os.getcwd(), dir_name, file_name)
initial_chat_history = converter.rawfile2chat(file_path)
print("-------- 初始 prompt 内容:")
print(initial_chat_history)

import configparser
from IPython import embed

from zhipuai import ZhipuAI

from ocr import ocr_img_text

class ChatStream(QThread):
    sign_response_text = pyqtSignal(tuple)
    def __init__(self, chat_history):
        super(ChatStream, self).__init__()
        self.messages = chat_history
    
    def run(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.client = ZhipuAI(api_key=config.get('zhipuai', 'api_key'))
        response = self.client.chat.completions.create(
            model="glm-4",  # 填写需要调用的模型名称
            messages=self.messages,
            stream=True,
        )
        for (i, chunk) in enumerate(response):
            self.sign_response_text.emit(tuple([i, chunk.choices[0].delta.content]))
        self.sign_response_text.emit(tuple([-1, '']))

class ChatBlock(QThread):
    sign_response_text = pyqtSignal(str)
    def __init__(self, chat_history):
        super(ChatBlock, self).__init__()
        self.messages = chat_history
    
    def run(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.client = ZhipuAI(api_key=config.get('zhipuai', 'api_key'))
        response = self.client.chat.completions.create(
            model="glm-4",  # 填写需要调用的模型名称
            messages=self.messages,
        )
        self.sign_response_text.emit(response.choices[0].message.content)

class ChatWindow(QWidget):
    def __init__(self):
        super(ChatWindow, self).__init__()
        self.setWindowTitle("chat")
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
        self.resize(900, 600)

        self.init_UI()

        # Chat history
        self.chat_history = []
        self.chat_history.extend(initial_chat_history)

        # is waiting for response
        self.is_waiting = False
        self.received_all = True

    def init_UI(self):
        # Display chat history
        self.chat_content = QTextBrowser(self)
        self.chat_content.setGeometry(30, 30, 840, 400)
 
        # Send text
        self.text_send = QPlainTextEdit(self)
        self.text_send.setGeometry(30, 460, 700, 100)
        self.text_send.setPlaceholderText("输入你的问题或需求···")

        # Send button
        self.btn_send = QPushButton('发送\n(Ctrl+Enter)', self)
        self.btn_send.clicked.connect(self.send_text)
        self.btn_send.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.btn_send.setGeometry(750, 460, 120, 40)
        
        # Cancel button
        self.btn_cancel = QPushButton('取消', self)
        self.btn_cancel.clicked.connect(self.close_window)
        self.btn_cancel.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.btn_cancel.setGeometry(750, 520, 120, 40)

        # Send key shortcut Ctrl+Enter
        self.send_key = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Return), self)
        self.send_key.activated.connect(self.send_text)
    
    def send_text(self):
        if self.is_waiting:
            return
        text_to_send = self.text_send.toPlainText()
        text_to_send_with_screen_content = text_to_send + "\n" + "屏幕内容：\n" + ocr_img_text()[0]
        self.chat_history.append({
            'role': 'user',
            'content': text_to_send_with_screen_content
        })
        self.is_waiting = True
        self.received_all = False
        self.chat_content.append(f'<span style=\" color: #ffffff;\">-- {text_to_send}</span>')
        self.text_send.clear()

        # Send text to the server in a new thread
        self.chat_thread = ChatStream(self.chat_history)
        self.chat_thread.sign_response_text.connect(self.receive_text_response)
        self.chat_thread.start()

    # Print the text received from the server word by word
    def receive_text_response(self, response):
        # Reiceive the first word of the response
        if response[0] == 0:
            self.receive_text(response[1])
        # Received the whole response
        elif response[0] == -1:
            self.received_all = True
            self.chat_history.append({
                'role': 'assistant',
                'content': self.text_receive
            })
        # Continue to receive the response
        else:
            self.receive_word(response[1])
    def receive_text(self, text):
        self.chat_content.append('-- ')
        self.text_timer = QTimer()
        self.receive_text_index = 0
        self.text_receive = text
        self.text_timer.timeout.connect(self.append_word)
        self.text_timer.start(50)
    def receive_word(self, word):
        self.text_timer = QTimer()
        self.text_receive += word
        self.text_timer.timeout.connect(self.append_word)
        self.text_timer.start(50)
    def append_word(self):
        if self.receive_text_index < len(self.text_receive):
            current_cursor = self.chat_content.textCursor()
            self.chat_content.moveCursor(current_cursor.End)
            self.chat_content.insertPlainText(self.text_receive[self.receive_text_index])
            self.receive_text_index += 1
        else:
            self.text_timer.stop()
            if self.received_all:
                self.is_waiting = False

    def close_window(self):
        self.close()