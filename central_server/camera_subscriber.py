import cv2
import zmq
import base64
import numpy as np
from datetime import datetime
import h5py
import os

class CameraSubscriber:
    def __init__(self, publisher_ports, output_dir, hdf5_file_path):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.running = True

        # Connect to multiple publisher ports
        for port in publisher_ports:
            self.socket.connect(f"tcp://localhost:{port}")

        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

        # Create an output directory if it doesn't exist
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Define the HDF5 file path
        self.hdf5_file_path = hdf5_file_path

    def save_frames_to_hdf5(self):
        # Open HDF5 file for writing
        with h5py.File(self.hdf5_file_path, 'w') as hdf5_file:
            timestamps_ds = hdf5_file.create_dataset('timestamps', (0,), maxshape=(None,), dtype=h5py.string_dtype())
            frames_ds = hdf5_file.create_dataset('frame_data', (0,), maxshape=(None,), dtype=h5py.string_dtype())

            while self.running:
                try:
                    # Receive the encoded frame
                    jpg_as_text = self.socket.recv_string(flags=zmq.NOBLOCK)

                    # Create a timestamp
                    timestamp = datetime.utcnow().isoformat()

                    # Append timestamp and frame data to the HDF5 datasets
                    timestamps_ds.resize((timestamps_ds.shape[0] + 1,))
                    frames_ds.resize((frames_ds.shape[0] + 1,))
                    timestamps_ds[-1] = timestamp
                    frames_ds[-1] = jpg_as_text
                except zmq.Again:
                    continue
                except Exception as e:
                    print(f"An error occurred while processing a frame: {e}")
                    break
            print("Exiting the loop and closing the HDF5 file.")

    def stop(self):
        self.running = False
        print("Camera subscriber stopped.")
