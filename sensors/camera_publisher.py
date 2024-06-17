import cv2
import zmq
import base64
import time

class CameraPublisher:
    def __init__(self, usb_camera_port_number, zmq_port, duration):
        self.usb_camera_port_number = usb_camera_port_number
        self.zmq_port = zmq_port
        self.duration = duration
        self.running = True

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{self.zmq_port}")

        self.cap = cv2.VideoCapture(self.usb_camera_port_number)

    def start_publishing(self):
        print(f"Camera publisher running on port {self.zmq_port} for {self.duration} seconds")
        count = 1
        start_time = time.time()
        while self.running and (time.time() - start_time) < self.duration:
            ret, frame = self.cap.read()
            if not ret:
                print(f"Camera not found at port {self.usb_camera_port_number}")
                break

            # Encode the frame as a JPEG image
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            
            # Publish the encoded frame
            self.socket.send_string(jpg_as_text)

            print(f"Frame {count} sent.")
            count += 1

        self.stop()

    def stop(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()
        print("Camera publisher stopped.")
