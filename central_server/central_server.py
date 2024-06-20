import zmq
import time
import threading
import cv2
import numpy as np

# CentralServer class
class CentralServer:
    def __init__(self, port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = port

    def start(self):
        self.socket.bind(f"tcp://*:{self.port}")
        print(f"Central server started on port {self.port}")

    def send_start_signal(self, duration=30, delay_start_seconds=10, sensor_id = "01"):
        # Calculate the future timestamp
        future_timestamp = time.time() + delay_start_seconds
        self.socket.send_json({"command": "START", "timestamp": future_timestamp, "sensor_id": sensor_id, "duration": duration})
        print(f"Sent start signal with timestamp {future_timestamp}")
