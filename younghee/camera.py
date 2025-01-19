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
            self.camera = cv2.VideoCapture(0)  # Change 0 to the appropriate index or device path
            if not self.camera.isOpened():
                logging.error("Failed to open camera.")

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            logging.info("Camera initialized")
        except Exception as e:
            logging.error(f"Error initializing camera: {e}")

    def capture_and_encode_image(self):
        try:
            logging.debug("Capturing image...")
            ret, frame = self.camera.read()
            if not ret:
                logging.error("Failed to capture image.")
                return None

            # Convert the image to base64
            _, buffer = cv2.imencode(".jpg", frame)
            image = base64.b64encode(buffer).decode("utf-8")
            return image
        except Exception as e:
            logging.error(f"Error capturing and encoding image: {e}")
            return None

    async def close(self):
        try:
            self.camera.release()
            logging.info("Camera released.")
        except Exception as e:
            logging.error(f"Error releasing camera: {e}")

if __name__ == "__main__":
    camera = Camera()
    image = camera.capture_and_encode_image()
    print(image)
    camera.close()