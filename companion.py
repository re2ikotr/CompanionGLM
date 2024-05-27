import os
import sys
import configparser
from PyQt5.QtGui import QMovie, QIcon, QImage, QPixmap, QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from qt_material import apply_stylesheet

from IPython import embed

from chat import ChatWindow, ChatBlock, initial_chat_history
from audio import AudioRecord, AudioPlay
from recognition import Recognition
from generation import Generation
from preferences import EditPreferences
from ocr import ocr_img_text

class Companion(QWidget):
    def __init__(self):
        super(Companion, self).__init__()
        # Init window settings
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Load image
        self.avatar = QLabel(self)
        self.avatar_path = 'resources/images/test/待机.gif'
        self.movie = QMovie(self.avatar_path)
        self.avatar.setMovie(self.movie)
        self.movie.start()

        # Resize window
        self.image = QImage(self.avatar_path)
        self.resize(self.image.width(), self.image.height())
        
        # Load tray icon
        self.icon_path = 'resources/icon/logo.png'
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(self.icon_path))
        self.tray_icon.show()

        # Create Menu
        self.menu = QMenu() 

        # Creating the menu options 
        self.chat_option = QAction("Chat")
        self.chat_option.triggered.connect(self.chat)
        self.menu.addAction(self.chat_option)

        self.preferences_option = QAction("Settings")
        self.preferences_option.triggered.connect(self.edit_preferences)
        self.menu.addAction(self.preferences_option)

        self.quit_option = QAction("Quit")
        self.quit_option.triggered.connect(self.quit)
        self.menu.addAction(self.quit_option)

        # Add menu to the tray
        self.tray_icon.setContextMenu(self.menu)

        # Prepare for dragging
        self.following_mouse = False

        # Record audio settings
        self.record = AudioRecord()
        self.btn_record = QPushButton('说话', self)
        self.btn_record.clicked.connect(self.change_record_status)

        # Speech recognition and generation
        # TODO: Add speech recognition and generation

        self.to_corner()
        self.show()

    # Move to bottom right corner when initialized
    def to_corner(self):
        screen_geo = QDesktopWidget().screenGeometry()
        self.move(screen_geo.width() - self.width() - 20, screen_geo.height() - self.height() - 60)
       
    # Dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.following_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
        elif event.button() == Qt.RightButton:
            self.menu.exec_(QCursor.pos())
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.following_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()
    def mouseReleaseEvent(self, event):
        self.following_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseDoubleClickEvent(self, event):
        self.chat()
    
    def quit(self):
        self.close()
        sys.exit()

    def chat(self):
        self.chat_window = ChatWindow()
        self.chat_window.move(self.pos().x() - self.chat_window.width() + 10,
                               self.pos().y() - self.chat_window.height() + 10)
        self.chat_window.show()

    # Record audio
    def change_record_status(self):
        if self.record.is_recording:
            self.record.is_recording = False
        else:
            self.record = AudioRecord()
            self.record.sign_stopped.connect(self.stop_record_received)
            self.record.is_recording = True
            self.record.start()
            self.btn_record.setText('停止')
    def stop_record_received(self, _):
        self.btn_record.setText('说话')
        self.send_for_recognition()
    
    # Speech recognition
    def send_for_recognition(self):
        self.recognition = Recognition()
        self.recognition.sign_recognition_text.connect(self.talk)
        self.recognition.start()

    # Pass the recognized text
    def talk(self, text):
        history = []
        history.extend(initial_chat_history)
        text_with_screen_content = text + "\n" + "屏幕内容：\n" + ocr_img_text()[0]
        history.append({
            'role': 'user',
            'content': text_with_screen_content,
        })
        self.chatblock = ChatBlock(history)
        self.chatblock.sign_response_text.connect(self.send_for_generation)
        self.chatblock.start()
    
    # Speech generation
    def send_for_generation(self, text):
        self.generation = Generation(text)
        self.generation.sign_audio_generated.connect(self.play_generated_audio)
        self.generation.start()
    def play_generated_audio(self, _):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.audioplay = AudioPlay('./data/audio/generated.wav')
        self.audioplay.start()

    # Edit preferences
    def edit_preferences(self):
        self.preferences = EditPreferences()
        self.preferences.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    pet = Companion()
    app.exec_()