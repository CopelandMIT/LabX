import time
import threading
from central_server.central_server import CentralServer

def run_server():
    # Initialize the central server on specified ports
    server = CentralServer(pub_port=5555, rep_port=5566)
    
    # Start the server
    server.start()
    
    # Wait a bit before sending the start signal to ensure nodes are listening
    time.sleep(2)
    
    # Send a start signal to all connected camera nodes
    server.send_start_signal(duration=10, delay_start_seconds=10, sensor_id="01", additional_info="Test run")

if __name__ == "__main__":
    # Run the server in its own thread to allow asynchronous operations
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    # Wait for the server thread to complete
    server_thread.join()
    
    print("Server operations completed.")
