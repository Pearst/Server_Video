from fastapi import FastAPI
import cv2
import numpy as np
import uvicorn  # Import uvicorn
from fastapi.responses import StreamingResponse

app = FastAPI()

# Video capture and frame generation
camera = cv2.VideoCapture(0)  # Use the default camera (change to a different index if necessary)

# Initialize flag to indicate whether to capture frames
capture_frames = True


def generate_frames():
    while capture_frames:
        success, frame = camera.read()
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


# Route to start capturing frames
@app.get("/start_capture")
async def start_capture():
    global capture_frames
    capture_frames = True
    return {"message": "Frame capture started"}


# Route to stop capturing frames
@app.get("/stop_capture")
async def stop_capture():
    global capture_frames
    capture_frames = False
    return {"message": "Frame capture stopped"}


if __name__ == "__main__":
    while True:
        try:
            # Run the FastAPI server using uvicorn
            uvicorn.run(app, host="127.0.0.1", port=8000)
        except KeyboardInterrupt:
            # Handle Ctrl+C to exit the server gracefully
            break
        finally:
            camera.release()
            cv2.destroyAllWindows()