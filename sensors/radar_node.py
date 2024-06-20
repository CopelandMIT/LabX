import zmq
import time
import threading

class RadarNode:
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
        # Wait until the specified timestamp to start data collection
        while time.time() < timestamp and not self.stop_event.is_set():
            time.sleep(0.1)

        start_time = time.time()
        while time.time() - start_time < duration and not self.stop_event.is_set():
            data = self.collect_radar_data()
            self.save_data_to_file(data, timestamp)

    def collect_radar_data(self):
        # Simulate radar data collection
        return "radar_data"

    def save_data_to_file(self, data, timestamp):
        filename = f'data_{timestamp}.txt'
        with open(filename, 'w') as f:
            f.write(data)
        print(f"Data saved to {filename}")

    def listen_for_start_signal(self):
        while True:
            message = self.socket.recv_json()
            if message["command"] == "START":
                self.start_data_collection(message["timestamp"], 60)
                break

if __name__ == "__main__":
    radar_node = RadarNode("central_server_ip_address")
    radar_node.connect_to_server()
    radar_node.listen_for_start_signal()
