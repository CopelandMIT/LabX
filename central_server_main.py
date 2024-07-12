import time
import threading
from central_server.central_server import CentralServer


def run_server():
    # Initialize the central server on specified ports
    server = CentralServer(pub_port=5555, router_port=5566)
    
    # Start the server
    server.run()
    
if __name__ == "__main__":
    # Run the server in its own thread to allow asynchronous operations
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    # Keep the main thread alive while the server is running
    while server_thread.is_alive():
        time.sleep(1)
    
    print("Server operations completed.")
