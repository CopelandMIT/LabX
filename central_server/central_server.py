import zmq
import time
import threading


class CentralServer:
    def __init__(self, ip="localhost", port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://{ip}:{port}")
        self.client_nodes = []  # List to store connected camera nodes (optional)

    def start(self):
        print("Central server started")

    def send_start_signal(self, future_seconds=0):
        # Send a JSON message with "command" and "timestamp" keys
        message = {"command": "START", "timestamp": time.time() + future_seconds}
        self.socket.send_json(message)
        print(f"Sent start signal to connected nodes (future seconds: {future_seconds})")

    def register_client_node(self, camera_node):
        # Add camera node to the list (optional)
        self.client_nodes.append(camera_node)