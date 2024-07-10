import time
import threading
import json
import paho.mqtt.client as mqtt


class MQTTCentralServer:
    def __init__(self, client_id="Central_Server", broker_address = "192.168.68.125") -> None:
        self.client_id = client_id
        self.broker_address = broker_address
        self.deployed_sensor_ids = ["0001", "0002"] # update to retrieve from SQL database/UI
        
        self.client = mqtt.Client(client_id=self.client_id)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.client.connect(self.broker_address)
        
        self.client.loop_start()
        
        time.sleep(1)
        
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"{self.client_id} is connected to the broker!")
            connection_confrimation_topics = [f"to_central_server/{deployed_sensor_id}/status/confirm_connection_response" for deployed_sensor_id in self.deployed_sensor_ids]
            update_topics = [f"to_central_server/{deployed_sensor_id}/status/update_from_sensor" for deployed_sensor_id in self.deployed_sensor_ids]
            finished_recording_topics = [f"to_central_server/{deployed_sensor_id}/status/finished_recording" for deployed_sensor_id in self.deployed_sensor_ids]
            alerts_topics = [f"to_central_server/{deployed_sensor_id}/status/alerts_from_sensors" for deployed_sensor_id in self.deployed_sensor_ids]
            all_topics = update_topics + finished_recording_topics + alerts_topics + connection_confrimation_topics
            self.subscribe_to_topics(all_topics)
        else:
            print(f"{self.client_id} unable to connect to broker. Return code: {rc}")
            
    def send_start_command(self, payload):
        self.client.publish("to_sensor/global/commands/start_recording", payload)
        print("sent START_RECORDING command to commands topic")
    
    def subscribe_to_topics(self, topics):
        if isinstance(topics, str):
            topics = [topics]
        for topic in topics:
            self.client.subscribe(topic=topic)
            print(f"{self.client_id} is subscribed to {topic}")    
        
    def on_message(self, client, userdata, msg):
        # create methods for different message topics and if/elif based on msg.topic.
        print(f"{self.client_id} recieved a message on topic {msg.topic}: {msg.payload.decode()}")
    
    def recording_in_process(self, stop_event, duration, time_delay):
        start_recording_time = time.time() + time_delay
        end_recording_time = time.time() + duration + time_delay
        while time.time() < start_recording_time:
            print(f"{round(start_recording_time - time.time())} seconds until recording starts.")
            time.sleep(1)
        print("Recording Started")
        while not stop_event.is_set() and time.time() < end_recording_time:
            time.sleep(.1) 
        if stop_event.is_set():
            print("Recording stopped by user")
        else:
            print("Recording Ended")
        
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print(f"Client {self.client_id} shutdown.")
        

def main():
    test_client = MQTTCentralServer()
    duration = int(input("How many seconds do you want to record for? "))
    time_delay = int(input("how many seconds do you want to delay the start time by? "))
    input("Press enter when ready to record")
    start_time = time.time()+time_delay
    
    payload = json.dumps({
    "command": "START_RECORDING", 
    "start_time": start_time,
    "duration": duration,
    "filename": "test" + str(start_time) + "_" + str(duration) + ".avi"})
    
    test_client.send_start_command(payload)
    stop_event = threading.Event()
    recording_thread = threading.Thread(target=test_client.recording_in_process, args=(stop_event, duration, time_delay))
    recording_thread.start()
    

if __name__ == "__main__":
    main()
    
    