import zmq
import time
import cv2
import threading

class CameraNode:
    def __init__(self, central_server_ip, central_server_port=5555):
        self.central_server_ip = central_server_ip
        self.central_server_port = central_server_port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.stop_event = threading.Event()

    def connect_to_server(self):
        self.socket.connect(f"tcp://{self.central_server_ip}:{self.central_server_port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '') 
        print("Connected to central server")

    def start_data_collection(self, timestamp, duration):
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f'data_{timestamp}.avi', fourcc, 20.0, (640, 480))

        # Wait until the specified timestamp to start data collection
        while time.time() < timestamp and not self.stop_event.is_set():
            time.sleep(0.1)

        start_time = time.time()
        while time.time() - start_time < duration and not self.stop_event.is_set():
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        cap.release()
        out.release()
        print(f"Data collection completed at {timestamp}")

    def listen_for_start_signal(self):
        while True:
            message = self.socket.recv_json()
            if message["command"] == "START":
                self.start_data_collection(message["timestamp"], 60)
                break
