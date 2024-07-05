import zmq
import time
import threading
import cv2
import numpy as np

# CentralServer class
class CentralServer:
    def __init__(self, pub_port=5555, rep_port=5566):
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_port = pub_port
        
        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_port = rep_port

    def start(self):
        try:
            self.pub_socket.bind(f"tcp://*:{self.pub_port}")
            print(f"Central server publisher started on port {self.pub_port}")
            
            self.rep_socket.bind(f"tcp://*:{self.rep_port}")
            print(f"Central server report socket started on port {self.rep_port}")
            
            threading.Thread(target=self.listen_for_acknoledgements).start()
        except Exception as e:
            print(f"Failed to start server: {e}")


    def send_start_signal(self, duration=30, delay_start_seconds=10, sensor_id = "01", additional_info=''):
        # Calculate the future timestamp
        delayed_start_timestamp = time.time() + delay_start_seconds
        self.pub_socket.send_json({
            "command": "START", 
            "delayed_start_timestamp": delayed_start_timestamp, 
            "sensor_id": sensor_id, 
            "duration": duration,
            "additional_info": additional_info})
        print(f"Sent start signal for camera file: CAM_{sensor_id}_{delayed_start_timestamp}_{duration}_{additional_info}.avi")


    def listen_for_acknoledgements(self):
        print("Thead started, listening for recieved signal")
        while True:
            message = self.rep_socket.recv_json()
            if message.get("status") == 'ACK':
                print(f"Recieved message from sensor ID {message['sensor_id']}: {message['message']}")
                self.rep_socket.send_json({"status":"OK"})