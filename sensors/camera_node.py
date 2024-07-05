import zmq
import time
import cv2
from datetime import datetime
import os

class CameraNode:
    def __init__(self, central_server_ip, 
                central_server_sub_port=5555, 
                central_server_req_port=5566):
        self.central_server_ip = central_server_ip
        self.sub_port = central_server_sub_port
        self.req_port = central_server_req_port

        self.sub_address = f"tcp://{self.central_server_ip}:{self.sub_port}"
        self.req_address = f"tcp://{self.central_server_ip}:{self.req_port}"

        self.context = zmq.Context()
        
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(self.sub_address)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

        self.req_socket = self.context.socket(zmq.REQ)
        self.req_socket.connect(self.req_address)

        print("Connected to central server")

            
    def listen_for_start_command(self):
        print("Listening for command")
        while True:
            message = self.sub_socket.recv_json()
            print(f"Raw message received: {message}")
            if message["command"] == "START":
                # Acknowledge the receipt of the START command
                self.acknowledge_command(sensor_id=message['sensor_id'])

                # Proceed to start data collection as per the command details
                self.start_data_collection(
                    delayed_start_timestamp=message["delayed_start_timestamp"], 
                    sensor_id=message['sensor_id'],
                    duration=message['duration'],
                    additional_info=message['additional_info'])
                break
        self.clean_up()
        

    def acknowledge_command(self, sensor_id):
        try:
            # Send an acknowledgment message to the central server
            self.req_socket.send_json({
                "status": "ACK",
                "sensor_id": sensor_id,
                "message": "Command received and processed."
            })
            # Wait for the server's reply to ensure the message was received
            response = self.req_socket.recv_json()
            print(f"Acknowledgment sent and confirmed by server: {response['status']}")
        except Exception as e:
            print(f"Failed to send acknowledgment: {e}")


    def start_data_collection(self, delayed_start_timestamp, sensor_id, duration, additional_info):
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        dt = datetime.fromtimestamp(delayed_start_timestamp)
        formatted_date = dt.strftime(f"%Y-%m-%d_%H%M%S{int(dt.microsecond / 1000):03d}")
        out = cv2.VideoWriter(f'/home/dcope/LabX/data/CAM_{sensor_id}_{formatted_date}_{duration}_{additional_info}.avi', fourcc, 20.0, (640, 480))

        # Wait until the specified timestamp to start data collection
        while time.time() < delayed_start_timestamp:
            time.sleep(0.01)

        start_time = time.time()
        print(f"Camera {sensor_id} Started at {formatted_date}")
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break
        print()

        cap.release()
        out.release()
        print(f"Data collection completed at {time.time()}")
        print(f"File saved: CAM_{sensor_id}_{formatted_date}_{duration}_{additional_info}.avi'")

    def clean_up(self):
        self.sub_socket.close()
        self.req_socket.close()
        self.context.term()
            # Check if display is available before attempting to use GUI functions
        if 'DISPLAY' in os.environ:
            cv2.destroyAllWindows()
