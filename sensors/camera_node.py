import zmq
import time
import cv2
import threading
import json

class CameraNode:
    def __init__(self, central_server_ip, 
                central_server_sub_port=5555, 
                central_server_router_port=5566):
        self.central_server_ip = central_server_ip
        self.sub_port = central_server_sub_port
        self.router_port = central_server_router_port

        self.sub_address = f"tcp://{self.central_server_ip}:{self.sub_port}"
        self.router_address = f"tcp://{self.central_server_ip}:{self.router_port}"
        
        self.context = zmq.Context()
        
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(self.sub_address)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

        self.router_socket = self.context.socket(zmq.DEALER)
        self.router_socket.setsocketopt(zmq.IDENTITY, b"001")
        self.router_socket.connect(self.router_address)

        print("Connected to central server")
        self.running = True

            
    def listen_for_start_command(self):
        while True:
            message = self.sub_socket.recv_json()
            message_data = json.loads(message)
            if message["command"] == "CONFIRM_CONNECTION":
                self.send_status("Ready")
            elif message["command"] == "START_RECORDING":
                # Acknowledge the receipt of the START command
                self.acknowledge_command(message_data)
                # Proceed to start data collection as per the command details
                self.start_data_collection(
                    delayed_start_timestamp=message["delayed_start_timestamp"], 
                    sensor_deployment_id=message['sensor_deployment_id'],
                    duration=message['duration'],
                    filename=message_data['filename'],
                    additional_info=message['additional_info'])
            elif message_data["command"] == "STATUS_UPDATE":
                self.send_status("Recording")
            elif message_data["command"] == "STOP_RECORDING":
                self.send_status("Completed")
                self.running = False
                

    def send_status(self, status):
        try: 
            self.router_socket.send_json({
                "status":status
            })
        except Exception as e:
            print(f"Failed to send status: {e}")

    def acknowledge_command(self, sensor_deployment_id):
        try:
            # Send an acknowledgment message to the central server
            self.router_socket.send_json({
                "status": "ACK",
                "sensor_deployment_id": sensor_deployment_id,
                "message": "Command received and processed."
            })
            # Wait for the server's reply to ensure the message was received
            response = self.router_socket.recv_json()
            print(f"Acknowledgment sent and confirmed by server: {response['status']}")
        except Exception as e:
            print(f"Failed to send acknowledgment: {e}")


    def start_data_collection(self, delayed_start_timestamp, sensor_id, duration, additional_info):
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f'CAM_{sensor_id}_{delayed_start_timestamp}_{duration}_{additional_info}.avi', fourcc, 20.0, (640, 480))

        # Wait until the specified timestamp to start data collection
        while time.time() < delayed_start_timestamp:
            time.sleep(0.01)

        start_time = time.time()
        print(f"Camera {sensor_id} Started")
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        cap.release()
        out.release()
        print(f"Data collection completed at {time.time()}")
        print(f"File saved: CAM_{sensor_id}_{str(delayed_start_timestamp)}_{duration}_{additional_info}.avi'")

