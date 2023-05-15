from djitellopy import tello
from threading import Thread
import cv2
import queue
from Recorder import Recorder
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from logger import Logger

class MinimalSubscriber:

    def __init__(self, record_path:str, log_path:str):

         # connect to the Drone
        self.me = tello.Tello()
        self.me.connect()

        self.recorder = Recorder(record_path)
        self.record_started = False
        self.record_thread = Thread(target=self.recorder.record)

        self.log = Logger(log_path, self.me)
        self.log_thread = Thread(target=self.log.update)

        # start the keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.tookoff = False
        self.listener.start()

        self.img = None
        self.cap: cv2.VideoCapture = self.me.get_video_capture()
        self.cap
        self.q = queue.Queue()

        # prints the Battery percentage
        print("Battery percentage:", self.me.get_battery())
        
        # if the battery is too low its arise an error
        if self.me.get_battery() < 10:
            raise RuntimeError("Tello rejected attemp to takeoff due to low Battery")


    def on_press(self, key):
        """
            This method allows the user to control 
            its drone using the keyboard.
            
            'space' - takeoff / land
            'b' - battery
            'e' - emergancy
            'up' - Up
            'down' - Down
            'left' - left
            'right' - right
            'w' - Forawrd
            's' - Backward
            'a/d' - YAW (ANGLE/DIRECTION)
            'r' - start recording
            'm' - save log file, unnecessary in case the record saved successfully
        """
        big_factor = 100
        medium_factor = 50
        
        a, b, c, d = 0, 0, 0, 0
        try:
            self.log.command = "STAND"
            # Takeoff
            if key == Key.space and not self.tookoff:
                self.tookoff = True
                self.me.takeoff()
                self.log.command = "TAKEOFF"
            # Land
            elif key == Key.space and self.tookoff:
                self.tookoff = False
                self.me.land()
                self.log.command = "LAND"
            # Up / Down
            elif key == Key.up:
                c = 0.5 * medium_factor
                self.recorder.state = 'UP'
                self.log.command = "UP"
            elif key == Key.down:
                c = -0.5 * medium_factor
                self.recorder.state = 'DOWN'
                self.log.command = "DOWN"
            # YAW
            elif key == Key.left:
                d = -0.5 * big_factor
                self.recorder.state = 'YAW LEFT'
                self.log.command = "YAW LEFT"
            elif key == Key.right:
                d = 0.5 * big_factor
                self.recorder.state = 'YAW RIGHT'
                self.log.command = "YAW RIGHT"
            
            # Forward / Backward
            elif key == KeyCode.from_char('w'):
                b = 0.5 * big_factor
                self.recorder.state = 'FORWARD'
                self.log.command = "FORWARD"
            elif key == KeyCode.from_char('s'):
                b = -0.5 * big_factor
                self.recorder.state = 'BACKWARD'
                self.log.command = "BACKWARD"
            # Left / Right
            elif key == KeyCode.from_char('a'):
                a = -0.5 * big_factor
                self.recorder.state = 'LEFT'
                self.log.command = "LEFT"
            elif key == KeyCode.from_char('d'):
                a = 0.5 * big_factor
                self.recorder.state = 'RIGHT'
                self.log.command = "RIGHT"
            # Battery
            elif key == KeyCode.from_char('b'):
                print("Battery percentage:", self.me.get_battery())
            # Record
            elif key == KeyCode.from_char('r') and not self.record_started:
                if self.record_started:
                    print("Already recording...")
                    pass
                # start both records and logger
                self.record_started = True
                self.record_thread.start()
                self.log_thread.start()
            # Emergency
            elif key == KeyCode.from_char('e'):
                try:
                    print("EMERGENCY")
                    self.me.emergency()
                except Exception as e:
                    print("Did not receive OK, reconnecting to Tello")
                    self.me.connect()

            elif key == KeyCode.from_char('m'):
                self.log.save_log()

            # send the commands to the drone
            self.me.send_rc_control(int(a), int(b), int(c), int(d))

        except AttributeError:
            print("irrelevant key")
            pass

    def on_release(self,key):
        self.recorder.state = None 
        self.me.send_rc_control(0, 0, 0, 0)


    def video(self):
        while True:
            try:
                image = self.q.get()
                cv2.imshow("results", image)
                cv2.waitKey(1)
            except queue.Empty:
                continue
    
    def stream(self):
        while True:
            ret, frame = self.cap.read()
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)


def main():
    rec_path = "example.wav"
    log_path = "example.csv"
    tello = MinimalSubscriber(rec_path, log_path)
    try:
        while True:
            continue
    finally:
        print("stopped.")
        print("Difference:",tello.recorder.record_start_time - tello.recorder.writedown_start_time)
        exit()

if __name__ == '__main__':
    main()
    