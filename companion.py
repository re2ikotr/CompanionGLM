import os
import sys
from PyQt5.QtGui import QMovie, QIcon, QImage, QPixmap, QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from qt_material import apply_stylesheet

from IPython import embed

from chat import ChatWindow

class Companion(QWidget):
    def __init__(self):
        super(Companion, self).__init__()
        # Init window settings
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Load image
        self.avatar = QLabel(self)
        self.avatar_path = 'resources/images/test/pathfinder2.png'
        self.movie = QMovie(self.avatar_path)
        self.avatar.setMovie(self.movie)
        self.movie.start()

        # resize window
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

        self.quit_option = QAction("Quit")
        self.quit_option.triggered.connect(self.quit)
        self.menu.addAction(self.quit_option)

        # Add menu to the tray
        self.tray_icon.setContextMenu(self.menu)

        # Prepare for dragging
        self.following_mouse = False

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    pet = Companion()
    app.exec_()