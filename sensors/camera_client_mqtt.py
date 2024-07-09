import paho.mqtt.client as mqtt
# import ssl
# import socket
import time
import threading

class CameraClientMQTT:
    def __init__(self, client_id, broker_address = "192.168.68.125", port=1883) -> None:
        self.port = port
        self.broker_address = broker_address
        self.client_id = client_id
        self.client = None


    def handle_mqtt_operations(self, stop_event):
        self.client = mqtt.Client(client_id=self.client_id)  
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start()       
            while stop_event.is_set():
                time.sleep(0.5)
        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"{self.client_id} is connected to broker!")
            self.subscribe_to_topics("commands")
        else:
            print(f"{self.client} unable to connect to broker with return code: {rc}")

    def on_message(self, client, userdata, msg):
        if msg.topic == "commands":
            print(f"Recieved message on {msg.topic}: {msg.payload.decode()}")
    
    def subscribe_to_topics(self, topics):
        if isinstance(topics, str):
            topics = [topics]
        for topic in topics:
            self.client.subscribe(topic=topic)
            print(f"{self.client_id} is subscribed to {topic}")


def main():
    stop_event = threading.Event()
    mqtt_client = CameraClientMQTT(client_id="001")
    mqtt_client_thread = threading.Thread(target=mqtt_client.handle_mqtt_operations, args=(stop_event,))
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
    