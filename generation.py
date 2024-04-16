import requests
import configparser

from PyQt5.QtCore import QThread, pyqtSignal

class Generation(QThread):
    sign_audio_generated = pyqtSignal(int)
    def __init__(self, text_to_generate):
        super(Generation, self).__init__()

        # Load configuration
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.base_url = config.get('backend', 'base_url')
        self.text_to_generate = text_to_generate
        self.generated_path = "./data/audio/generated.wav"
    
    def run(self):
        response = requests.post(self.base_url + "generation/", data=self.text_to_generate.encode('utf-8'))
        response_audio = requests.get(self.base_url + "static/response.wav")
        with open(self.generated_path, 'wb') as f:
            f.write(response_audio.content)
        self.sign_audio_generated.emit(0)