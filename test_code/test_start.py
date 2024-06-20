import ntplib
import zqm
from time import time, ctime, sleep
import sys
import threading

class ZQMSubStart():
    def __init__(self, central_server_ip, central_server_port) -> None:
        self.central_server_ip = central_server_ip
        self.central_port = central_server_port

        self.context = zqm.Context()
        self.sub_socket = self.context.socket(zqm.SUB)
        self.connect_to_server()

        self.stop_event = threading.Event()

    def connect_to_server(self):
        self.socket.connect(f"tcp://{self.central_server_ip}:{self.central_port}")        
        self.setsockopt_string(zqm.SUBSCRIBE,'')
        print("Connected to central server")



    def listen_for_start_signal(self):
        while 
