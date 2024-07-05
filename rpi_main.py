from sensors.camera_node import CameraNode

def run_camera_node():
    # Set up the camera node with the central server's IP address and ports
    node = CameraNode(central_server_ip='192.168.68.100',  # Change to your server's actual IP address
                      central_server_sub_port=5555,
                      central_server_req_port=5566)
    
    # Start listening for commands indefinitely
    node.listen_for_start_command()

if __name__ == "__main__":
    # Start the camera node operations
    run_camera_node()
    print("Camera node operations completed.")
