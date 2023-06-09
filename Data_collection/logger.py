from threading import Thread
import pandas as pd
import djitellopy
import time


class Logger:

    def __init__(self, filename: str, tello: djitellopy.Tello):
        
        self.filename = filename
        self.tello = tello
        # self.df = pd.DataFrame(columns=['time', 'label', 'baro', 'pitch', 'roll', 'Yaw', 'height', 'Vx', 'Vy', 'Vz', 'battery'])
        self.df = pd.DataFrame(columns=['time', 'label'])
        self.command = "0"
        # self.thread_update = Thread(target=self.update).start()
        self.roll = 0
        self.yaw = 0
        self.start_time = None
        


    def add(self, data: dict):
        """
            Given a list of all parametrs, add them to the DF.
        """
        if self.start_time is None:
            self.start_time = time.time()

        # Extract the desired parameters from the state dict
        curr_time = time.time() - self.start_time
        if data:
            roll = data['roll']
            pitch = data['pitch']
            yaw = data['yaw']
            height = data['h']
            vx = data['vgx']
            vy = data['vgy']
            vz = data['vgz']
            battery = data['bat']
            baro = data['baro']

        # if self.command == "0" and \
        #     abs(self.yaw - yaw) > 20:
        #         print("YAW HIT!!", abs(self.yaw - yaw))
        #         self.command = "1"

        # elif self.command == "0" and \
        #     abs(self.yaw - yaw) > 10:
        #         print("YAW Stabilization!!", abs(self.yaw - yaw))
        #         self.command = "1"
        
        # elif self.command == "0" and \
        #     abs(self.roll - roll) > 5:
        #         print("ROLL HIT!!", abs(self.roll - roll))
        #         self.command = "1"
        
        # self.roll = roll      
        # self.yaw = yaw

        # create a row from the above values
        if data:
            row = [curr_time, self.command, baro, pitch, roll, yaw, height, vx, vy, vz, battery]    
        else:
            row = [curr_time, self.command]
        # save the currnet state in the log 
        self.df.loc[len(self.df)] = row
        # restart the command to: STAND

    
    def save_log(self):
        """
            This method saves the data frame to a csv file.
        """
        print("save!")
        self.df.to_csv(self.filename)
    
    def update(self):
        """
            This thread update the log file every 0.5 seconds.
        """
        while True:
            time.sleep(0.1)
            # state = self.tello.get_current_state()
            state = None
            self.add(state)
    


