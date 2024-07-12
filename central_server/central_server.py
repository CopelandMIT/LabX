import zmq
import time
import threading
import json

class CentralServer:
    def __init__(self, pub_port=5555, router_port=5566):
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_port = pub_port
        self.pub_socket.bind(f"tcp://*:{self.pub_port}")
        print(f"Central server publisher started on port {self.pub_port}")
        
        self.router_socket = self.context.socket(zmq.ROUTER)
        self.router_port = router_port
        self.router_socket.bind(f"tcp://*:{self.router_port}")
        print(f"Central server report socket started on port {self.router_port}")
        
        self.running = True
        self.sensor_statuses = {"001": "Offline"}
        self.receive_thread = None
        
        # Run receive thread
        self.receive_thread = threading.Thread(target=self.receive_message)
        self.receive_thread.start()
        self.print_sensor_statuses()

    def confirm_central_server_to_node_connection(self):
        """Run startup configuration tasks."""
        # Confirm connections with sensor nodes
        time.sleep(1)
        self.send_command("CONFIRM_CONNECTION")
        print("Confirm Connection message sent.")
        
    def update_status(self, sensor_deployment_id, status):
        self.sensor_statuses[sensor_deployment_id] = status
        print(f"Updated status for sensor_deployment_id {sensor_deployment_id}: {status}")
        
    def send_command(self, command, data=None):
        if data is None:
            data = {}
        message = json.dumps({"command": command, **data})
        self.pub_socket.send_string(message)
        print(f"Published command: {command} on tcp://*:{self.pub_port}")
    
    def receive_message(self):
        while self.running:
            try:
                identity, message = self.router_socket.recv_multipart(flags=zmq.NOBLOCK)
                sensor_deployment_id = identity.decode('utf-8')
                message = message.decode('utf-8')
                data = json.loads(message)
                if 'status' in data:
                    self.update_status(sensor_deployment_id, data['status'])
                print(f"Received message from sensor deployment id {sensor_deployment_id}: {message}")
            except zmq.Again:
                time.sleep(0.1)
            except zmq.ZMQError as e:
                print(f"ZMQ Error: {e}")
                self.running = False
    
    def start_recording(self, duration=10, delay_start_seconds=2, sensor_deployment_id="001", filename="test_video_", additional_info=""):
        """Start the data capture session."""
        # Calculate the future timestamp
        start_timestamp = time.time() + delay_start_seconds
        filename = filename + str(start_timestamp)
        self.send_command("START_RECORDING", {
            "filename": filename,
            "delayed_start_timestamp": start_timestamp,
            "sensor_deployment_id": sensor_deployment_id,
            "duration": duration,
            "additional_info": additional_info
        })
        print(f"Sent start signal for camera file: CAM_{sensor_deployment_id}_{start_timestamp}_{duration}_{additional_info}.avi")
        return start_timestamp

    def run(self):
        # Start recording
        duration = 10
        delay_start_seconds = 5
        start_timestamp = self.start_recording(duration=duration, delay_start_seconds=delay_start_seconds)
        end_timestamp = start_timestamp + duration
        
        # Check Status Updates and wait for recording to finish
        while time.time() < end_timestamp:
            self.send_command("STATUS_UPDATE")
            time.sleep(1)
            self.print_sensor_statuses()
            
        # Wait for metadata
        time.sleep(2)
        
        # Print final sensor statuses
        self.print_sensor_statuses()
        
        self.running = False
        if self.receive_thread:
            self.receive_thread.join()
    
    def print_sensor_statuses(self):
        print("Sensor statuses:")
        for sensor_deployment_id, status in self.sensor_statuses.items():
            print(f"{sensor_deployment_id}: {status}")
