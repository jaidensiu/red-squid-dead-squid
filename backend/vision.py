import cv2
import numpy as np
from collections import deque

class MotionDetector:
    def __init__(self, frames_to_persist=5, min_area=750, blur_kernel=(11, 11), threshold=30):
        self.frames_to_persist = frames_to_persist
        self.min_area = min_area
        self.blur_kernel = blur_kernel
        self.threshold = threshold
        self.frame_queue = deque(maxlen=frames_to_persist)
        self.delay_counter = 0
        self.first_frame = None
        self.next_frame = None

    def process_frame(self, frame):
        # Convert and blur the frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, self.blur_kernel, 0)

        # Initialize first frame for comparison
        if self.first_frame is None:
            self.first_frame = gray
            return []

        self.delay_counter += 1
        if self.delay_counter > self.frames_to_persist:
            self.delay_counter = 0
            self.first_frame = self.next_frame

        # Set the next frame to compare (the current frame)
        self.next_frame = gray

        # Calculate the absolute difference between frames
        frame_diff = cv2.absdiff(self.first_frame, self.next_frame)
        _, thresh = cv2.threshold(frame_diff, self.threshold, 255, cv2.THRESH_BINARY)

        # Dilate the thresholded image to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter out small contours
        motion_contours = [contour for contour in contours if cv2.contourArea(contour) > self.min_area]
        return motion_contours

if __name__ == "__main__":
    motion_detector = MotionDetector()

    # Process frames from video capture
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    camera.set(cv2.CAP_PROP_FPS, 30)

    while True:
        ret, frame = camera.read()
        if ret:
            contours = motion_detector.process_frame(frame)
            for contour in contours:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow("Motion Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
