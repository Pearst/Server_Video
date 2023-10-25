import os
import requests
from PIL import Image
from io import BytesIO
import time
import cv2
import numpy as np

# Server configuration
server_url = "http://localhost:8000/start_capture"  # URL to start frame capture

# Directory to save frames in the same directory as the script
output_directory = os.path.dirname(os.path.abspath(__file__))

# Video output path
output_video_path = os.path.join(output_directory, "captured_video.avi")

# Recording duration in seconds
record_duration = 10  # 10 seconds

# Define the video codec and frame rate
fourcc = cv2.VideoWriter_fourcc(*'XVID')
frame_rate = 20

# Initialize the video writer
video_writer = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (640, 480))

start_time = time.time()
end_time = start_time + record_duration


def save_frames():
    try:
        # Start frame capture on the server
        response = requests.get(server_url)
        if response.status_code == 200:
            while time.time() < end_time:
                try:
                    response = requests.get("http://localhost:8000/video_feed", stream=True)
                    if response.status_code == 200:
                        frame_bytes = b""
                        for chunk in response.iter_content(chunk_size=1024):
                            frame_bytes += chunk
                            a = frame_bytes.find(b'\xff\xd8')
                            b = frame_bytes.find(b'\xff\xd9')
                            if a != -1 and b != -1:
                                jpg = frame_bytes[a:b + 2]
                                frame_bytes = frame_bytes[b + 2:]

                                # Convert image to a NumPy array
                                image = np.array(Image.open(BytesIO(jpg)))
                                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                                video_writer.write(image)
                    else:
                        print(f"Error fetching frames. Status code: {response.status_code}")
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(1)  # Wait for a moment before retrying
        # Stop frame capture on the server
        response = requests.get("http://localhost:8000/stop_capture")
    except Exception as e:
        print(f"Error: {e}")

    # Release the video writer and close the video file
    video_writer.release()

if __name__ == "__main__":
    save_frames()
    print(f"Video saved to: {output_video_path}")
