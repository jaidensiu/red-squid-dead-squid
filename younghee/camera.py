import base64
import cv2
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)

    async def capture_and_encode_image(self):
        logging.info("Capturing image...")
        ret, frame = self.camera.read()
        if not ret:
            logging.error("Failed to capture image.")
            return None

        # Convert the image to base64
        _, buffer = cv2.imencode(".jpg", frame)
        image = base64.b64encode(buffer).decode("utf-8")
        return image

    async def close(self):
        self.camera.release()
        logging.info("Camera released.")
