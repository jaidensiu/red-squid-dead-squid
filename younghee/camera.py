import base64
import cv2
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

class Camera:
    def __init__(self):
        try:
            self.camera = cv2.VideoCapture(0)
        except Exception as e:
            logging.error(f"Failed to initialize camera: {e}")
            return

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.capture_and_encode_image()

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
