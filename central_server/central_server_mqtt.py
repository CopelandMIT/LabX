import time
import threading
import json
import paho.mqtt.client as mqtt


class MQTTCentralServer:
    def __init__(self, client_id="Central_Server", broker_address = "192.168.68.125") -> None:
        self.client_id = client_id
        self.broker_address = broker_address
        self.deployed_sensor_ids = ["0001", "0002"] # update to retrieve from SQL database/UI
        self.deployed_sensor_statuses = {deployed_sensor_id: "Not Connected" for deployed_sensor_id in self.deployed_sensor_ids}
        self.deployed_sensors_last_heartbeat = {deployed_sensor_id: time.time()-1e6 for deployed_sensor_id in self.deployed_sensor_ids}
        # Define topics
        self.topics = {
            'heartbeat': "to_central_server/+/status/heartbeats_from_sensors",
            'confirm_connection': "to_central_server/+/status/confirm_connection",
            'started_recording': "to_central_server/+/status/started_recording",
            'finished_recording': "to_central_server/+/status/finished_recording",
            'alerts': "to_central_server/+/status/alerts_from_sensors",
            'updates': "to_central_server/+/status/updates_from_sensors"
        }
        
        self.client = mqtt.Client(client_id=self.client_id)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.stop_event = threading.Event()
 
# CENTRAL SERVER MQTT SET UP
        
    def run_mqtt_operations(self):
        self.client.connect(self.broker_address)
        self.client.loop_start()
        
        # mqtt thread loop
        while not self.stop_event.is_set():
            time.sleep(1)
            
        # Disconnect Function called.     
        self.client.loop_stop()
        self.client.disconnect()
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"{self.client_id} is Connected to MQTT Broker")
            # Subscribe to all defined topics
            for key, topic in self.topics.items():
                self.client.subscribe(topic)
                print(f"Subscribed to {topic}")       
        else:
            print(f"{self.client_id} unable to connect to broker. Return code: {rc}")
    
    
    def subscribe_to_topics(self):
        '''called in on_connect, to subscribe to all topics for each deployed sensor'''
        for topic, qos in self.topics:
            try:
                self.client.subscribe(topic=topic, qos=qos)
            except Exception as e:
                print(f"Failed to subscribe to {topic}: {e}")
            else:
                print(f"{self.client_id} is subscribed to {topic}")   
            
    def on_message(self, client, userdata, msg):
        # print(f"{self.client_id} received a message on topic {msg.topic}: {msg.payload.decode()}")
        try:
            payload = json.loads(msg.payload.decode())  # Assuming payload is JSON encoded
        except json.JSONDecodeError:
            print("Failed to decode JSON payload")
            return

        # Extracting the sensor ID from the topic
        # Topic format is "to_central_server/{deployed_sensor_id}/status/{status_type}"
        parts = msg.topic.split('/')
        if len(parts) < 4:
            print("Unexpected topic format")
            return
        deployed_sensor_id = parts[1]
        status_type = parts[3]

        # Dispatch actions based on the status_type part of the topic
        if status_type == "confirm_connection":
            self.handle_confirm_connection(deployed_sensor_id, payload)
        elif status_type == "started_recording":
            self.handle_started_recording(deployed_sensor_id, payload)
        elif status_type == "finished_recording":
            print("recieved recording finished message")
            self.handle_finished_recording(deployed_sensor_id, payload)
        elif status_type == "heartbeats_from_sensors":
            self.handle_heartbeat(deployed_sensor_id, payload)
        elif status_type == "alerts_from_sensors":
            self.handle_alerts(deployed_sensor_id, payload)
        elif status_type == "updates_from_sensors":
            self.handle_updates(deployed_sensor_id, payload)
        else:
            print(f"Unhandled topic {msg.topic}")
    
    def disconnect(self):
        self.stop_event.set()
        print(f"Client {self.client_id} shutdown.")
  
#CONFRIM CONNECTION WITH SENSORS  
    
    def confirm_sensor_connections(self):
        '''called immedately after on_connect or with a UI button'''
        print(f"Confirming Connections from Sensors: {self.deployed_sensor_ids}")
        for deployed_sensor_id in self.deployed_sensor_ids:
            self.client.publish(
                f"to_sensor/{deployed_sensor_id}/commands/confirm_connection", 
                payload=json.dumps("CONFRIM_CONNECTION"),
                qos=2)
            print(f"Confrim connection message sent to {deployed_sensor_id}")
            
    def handle_confirm_connection(self, deployed_sensor_id, payload):
        print(f"Confirm connection recieved from {deployed_sensor_id}")

#HEARTBEAT FROM SENSORS 

    def handle_heartbeat(self, deployed_sensor_id, payload):
        self.deployed_sensors_last_heartbeat[deployed_sensor_id] = payload['heartbeat_time']

    def monitor_sensors_heartbeat_thread(self):
        while True:
            time.sleep(10)
            current_time = time.time()
            for deployed_sensor_id, last_heartbeat in self.deployed_sensors_last_heartbeat.items():
                if current_time - last_heartbeat > 30:  # 30 seconds threshold
                    pass
                    #print(f"Sensor {deployed_sensor_id} might be disconnected.")
                    #TODO Trouble shoot reconnection to sensor. 
                        
#STATUS UPDATES FROM SENSORS   

    def request_sensor_status(self):
        print(f"Requesting Status from Sensors: {self.deployed_sensor_ids}")
        for deployed_sensor_id in self.deployed_sensor_ids:
            self.client.publish(
                f"to_sensor/{deployed_sensor_id}/commands/updates_from_sensors", 
                payload=json.dumps("Send Status to Central Server"),
                qos=2)
            print(f"Status request message sent to {deployed_sensor_id}")

    def handle_updates(self, deployed_sensor_id, payload):
        print(f"recieved update from sensor {deployed_sensor_id} : {payload}")
        self.deployed_sensor_statuses[deployed_sensor_id] = payload['status']

#START RECORDING
            
    def send_global_start_recording(self, payload):
        self.client.publish("to_sensor/global/commands/start_recording", payload)
        print("sent START_RECORDING to to_sensor/global/commands/start_recording")
        
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
    
    def handle_started_recording(self, deployed_sensor_id, payload):
        print(f"{deployed_sensor_id} has started recording")       

# END RECORDING

    def handle_finished_recording(self, deployed_sensor_id, payload):
        print(f"{deployed_sensor_id} has finished recording")     
        #TODO save payload data about file information 
        print(payload)

# HANDLE ALERTS

    def handle_alerts(self, deployed_sensor_id, payload):
            print(f"{deployed_sensor_id} has sent an alert")     
            #TODO save payload data about file information 
            print(payload) 

# MAIN CENTRAL SERVER TESTING        

def main():
    test_client = MQTTCentralServer()
    mqtt_thread = threading.Thread(target=test_client.run_mqtt_operations, daemon=True)
    mqtt_thread.start()
    time.sleep(2)  # Give some time for MQTT setup and connections
    test_client.confirm_sensor_connections()
    time.sleep(1)
    threading.Thread(target=test_client.monitor_sensors_heartbeat_thread, daemon=True).start()
    time.sleep(0.5)
    
    try:
        while True:
            duration = int(input("How many seconds do you want to record for? "))
            time_delay = int(input("how many seconds do you want to delay the start time by? "))
            input("Press enter when ready to record")
            start_time = time.time()+time_delay
            
            payload = json.dumps({
            "delayed_start_timestamp": start_time,
            "duration": duration,
            "filename": "test" + str(start_time) + "_" + str(duration),
            "additional_info": ""})
            
            test_client.send_global_start_recording(payload)
            stop_event = threading.Event()
            recording_thread = threading.Thread(
                target=test_client.recording_in_process, 
                args=(stop_event, duration, time_delay), daemon=True)
            recording_thread.start()
           
            time.sleep(duration + time_delay + 1.5)
            if recording_thread.is_alive():
                recording_thread.join()
                   
            continue_recording = input("Start another recording? (yes or no)")
            if continue_recording.lower() not in ("yes", "yes ", "y"):
                time.sleep(1) # Ensure file writing has time. 
                print("Exiting Recording Sesion")
                break

    except KeyboardInterrupt:
        #TODO send command to sensors to stop recording. 
        print("Program ended by user")
    finally:
        test_client.stop_event.set()
        if recording_thread.is_alive():
            recording_thread.join()
        if mqtt_thread.is_alive():
            mqtt_thread.join()
        test_client.disconnect()    

if __name__ == "__main__":
    main()
    
    