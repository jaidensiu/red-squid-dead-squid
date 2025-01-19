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

    def detect_bodies(self, frame):
        # Use HOG descriptor or a pre-trained model to detect bodies
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        # Detect people in the frame
        bodies, _ = hog.detectMultiScale(frame, winStride=(8, 8))

        return bodies

    def identify_players(self, motion_contours, frame):
        bodies = self.detect_bodies(frame)
        player_motions = []

        for motion in motion_contours:
            motion_moment = cv2.moments(motion)
            if motion_moment['m00'] == 0:
                continue

            motion_centroid = (
                int(motion_moment['m10'] / motion_moment['m00']),
                int(motion_moment['m01'] / motion_moment['m00'])
            )

            # Find the closest body to the motion centroid
            closest_body = None
            min_distance = float('inf')

            for (x, y, w, h) in bodies:
                body_centroid = (x + w // 2, y + h // 2)
                distance = np.linalg.norm(np.array(motion_centroid) - np.array(body_centroid))

                if distance < min_distance:
                    min_distance = distance
                    closest_body = (x, y, w, h)

            if closest_body is not None:
                player_motions.append({
                    'motion_centroid': motion_centroid,
                    'body_box': closest_body
                })

        return player_motions


if __name__ == "__main__":
    motion_detector = MotionDetector()

    # Process frames from video capture
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    camera.set(cv2.CAP_PROP_FPS, 30)

    while True:
        ret, frame = camera.read()
        if ret:
            # Process the frame for motion and body detection
            contours = motion_detector.process_frame(frame)
            bodies = motion_detector.detect_bodies(frame)

            # Create separate frames for motion contours and body detections
            motion_frame = frame.copy()
            # body_frame = frame.copy()

            # draw motion contours in motion frame as the contour, using draw contours
            for contour in contours:
                cv2.drawContours(motion_frame, [contour], -1, (0, 255, 0), 2)

            # Highlight detected bodies on body_frame
            for (x, y, w, h) in bodies:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Combine the two frames side by side
            combined_frame = np.hstack((motion_frame, frame))


            # Display the combined frame
            cv2.imshow("Motion Contours (Left) | Body Detection (Right)", combined_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Release resources
    camera.release()
    cv2.destroyAllWindows()

