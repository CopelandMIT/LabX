import threading
import json
import os
import time
import cv2
import paho.mqtt.client as mqtt

class CameraClientMQTT:
    def __init__(self, client_id, broker_address = "192.168.68.125", port=1883) -> None:
        self.port = port
        self.broker_address = broker_address
        self.client_id = client_id
        self.deployed_sensor_id = client_id
        self.client = None
        self.stop_event = threading.Event()


    def handle_mqtt_operations(self):
        self.client = mqtt.Client(client_id=self.client_id)  
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start()       
            while not self.stop_event.is_set():
                time.sleep(1)
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            print("Disconnected from broker.")        


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"{self.client_id} is connected to broker!")
            self.subscribe_to_topics(["to_sensor/global/commands/start_recording",
                                      "to_sensor/global/commands/stop_recording",
                                      f"to_sensor/{self.deployed_sensor_id}/commands/confirm_connection",
                                      f"to_sensor/{self.deployed_sensor_id}/commands/start_recording",
                                      f"to_sensor/{self.deployed_sensor_id}/commands/stop_recording",
                                      f"to_sensor/{self.deployed_sensor_id}/commands/status_update_request"])
        else:
            print(f"{self.client} unable to connect to broker with return code: {rc}")

    def on_message(self, client, userdata, msg):
        # confirm_connection logic
        if "confirm_connection" in msg.topic:
            print(f"Central Server to {self.deployed_sensor_id} connection confrimed!")
            self.client.publish(f"to_central_server/{self.deployed_sensor_id}/status/confirm_connection", str({self.deployed_sensor_id}), qos=2)
        # start_recording logic
        elif "start_recording" in msg.topic:
            print(f"Recieved message on {msg.topic}: {msg.payload.decode()}")
            self.client.publish(f"to_central_server/{self.deployed_sensor_id}/status/update_from_sensor", json.dumps({"deployed_sensor_id":self.deployed_sensor_id, "message":"Recording Started"}), qos=2)
            recording_instructions_from_central_server = json.loads(msg.payload)
            self.start_recording(recording_instructions_from_central_server)
        # status_update_request logic
        # stop_recording logic

    
    def subscribe_to_topics(self, topics):
        if isinstance(topics, str):
            topics = [topics]
        for topic in topics:
            self.client.subscribe(topic=topic)
            print(f"{self.client_id} is subscribed to {topic}")

    def start_recording(self, message_data):
        delayed_start_timestamp = message_data['delayed_start_timestamp']
        sensor_deployment_id = self.deployed_sensor_id
        duration = message_data['duration']
        filename = message_data['filename']
        additional_info = message_data['additional_info']

        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        data_directory = os.path.join(os.getcwd(), 'data')
        filepath = os.path.join(data_directory, f"{filename}.avi")
        out = cv2.VideoWriter(filepath, fourcc, 20.0, (640, 480))

        # Wait until the specified timestamp to start data collection
        while time.time() < delayed_start_timestamp:
            time.sleep(0.01)

        start_time = time.time()
        print(f"Camera {sensor_deployment_id} Recording Started")
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        cap.release()
        out.release()
        print(f"Data collection completed at {time.time()}")
        print(f"File saved: {filepath}")
        filesize = self.get_file_size(filepath)
        self.send_finished_recording_to_central_server(filename, filesize=filesize)
        

    def get_file_size(self, file_path):
        '''Return the file size'''
        try:
            size = os.path.getsize(file_path)
            return size
        except OSError as e:
            print(f"Error: {e}")
            return None

    def send_finished_recording_to_central_server(self, filename, filesize):
        #TODO include file size etc.
        self.client.publish(f"to_central_server/{self.deployed_sensor_id}/status/finished_recording", json.dumps({"deployed_sensor_id":self.deployed_sensor_id, "filename":filename,
        "file_size": filesize}), qos=2)

def main():
    stop_event = threading.Event()
    mqtt_client = CameraClientMQTT(client_id="0001")
    mqtt_client_thread = threading.Thread(target=mqtt_client.handle_mqtt_operations)
    mqtt_client_thread.start()

    try: 
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Program interupted")
        stop_event.set()
        mqtt_client_thread.join()

if __name__ == "__main__":
    main()
    