# camera_publisher.py
import cv2
import zmq
import base64
import numpy as np

usb_camera_port_number = 0

print(usb_camera_port_number)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

# Capture Video Data from USB Webcam
cap = cv2.VideoCapture(usb_camera_port_number)

print("Running")

while True:
    ret, frame = cap.read()
    if not ret:
        print(f"Camera not found at {usb_camera_port_number}")                
        break

    print("Found USB camera")

    #encode the frame as a JPEG image
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    
    #Publish the encoded frame
    socket.send_string(jpg_as_text)

    #disply the frame locally
    cv2.imshow('Publisher', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# realease the capture and close the windows
cap.release()
cv2.destroyAllWindows()
