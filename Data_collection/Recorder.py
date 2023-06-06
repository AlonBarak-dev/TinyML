import pyaudio
import wave
import time
from threading import Thread
from logger import Logger

class Recorder():
    def __init__(self, file_path:str, log:Logger):
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 1
        self.fs = 16000  # Record at 16000 samples per second
        self.seconds = 120
        self.state = None
        self.record_start_time = None
        self.writedown_start_time = None
        self.file_path = file_path
        self.log = log

    def record(self):
        """
            This method generate the data - record .wav files.
        """
        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        stream = p.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer=self.chunk,
                        input=True,
                        input_device_index=1)

        frames = []  # Initialize array to store frames
        print('Started recording...')
        # Store data in chunks for 3 seconds
        self.record_start_time = time.time()
        for i in range(0, int((self.fs / self.chunk) * self.seconds)):
            data = stream.read(self.chunk)
            frames.append(data)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()
        print('FINISHED RECORDING!!!!!!!!!!!!!!!!!!!!!!!!!!!')

        # save the log file
        self.log.save_log()

        # Save the recorded data as a WAV file
        wf = wave.open(self.file_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(frames))
        wf.close()
        
    