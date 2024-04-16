import pyaudio
import simpleaudio as sa
import wave
import time

from PyQt5.QtCore import QThread, pyqtSignal

class AudioRecord(QThread):
    sign_stopped = pyqtSignal(int)
    def __init__(self):
        super(AudioRecord, self).__init__()
        # Record settings
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.RECORD_SECONDS = 20
        self.WAVE_OUTPUT_FILENAME = "./data/audio/record.wav"

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Control start and stop of recording
        self.is_recording = False
        self.start_time = 0
        
        
    # Start recording
    def start_record(self):
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                      rate=self.RATE, input=True,
                                      frames_per_buffer=self.CHUNK)
        self.frames = []
        self.start_time = time.time()
        while self.is_recording and time.time() - self.start_time < self.RECORD_SECONDS:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)

    def save_record(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        self.is_recording = False
        self.sign_stopped.emit(0)

    def run(self):
        self.start_record()
        self.save_record()

class AudioPlay(QThread):
    sign_stopped = pyqtSignal(int)
    def __init__(self, audio_path):
        super(AudioPlay, self).__init__()
        self.audio_path = audio_path

    def stop(self):
        self.play_obj.stop()
        self.sign_stopped.emit(0)

    def run(self):
        self.wave_obj = sa.WaveObject.from_wave_file(self.audio_path)
        self.play_obj = self.wave_obj.play()
        self.play_obj.wait_done()
        self.sign_stopped.emit(0)