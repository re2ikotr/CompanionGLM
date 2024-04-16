import requests
import configparser

from PyQt5.QtCore import QThread, pyqtSignal

class Recognition(QThread):
    sign_recognition_text = pyqtSignal(str)
    def __init__(self):
        super(Recognition, self).__init__()

        # Load configuration
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.audio_path = "./data/audio/record.wav"
        self.base_url = config.get('backend', 'base_url')
        
    def run(self):
        with open(self.audio_path, 'rb') as f:
            audio_data = f.read()
        response = requests.get(self.base_url + "recognition/", data=audio_data)
        data = response.content.decode('unicode_escape')
        self.sign_recognition_text.emit(data)