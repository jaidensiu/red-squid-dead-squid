import time
import cv2
import numpy as np
from collections import deque
import random

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
        self.player_regions = []

    def set_regions(self, num_players):
        self.player_regions = []
        total_width = 960
        region_width = total_width // num_players
        for i in range(num_players):
            self.player_regions.append((current_index, current_index + region_width))
            current_index += region_width

    def get_label(self, contour):
        # get centroid`` of contour
        M = cv2.moments(contour)
        if M["m00"] == 0:
            return ""
        cX = int(M["m10"] / M["m00"])
        for i in range (len(self.player_regions)):
            region = self.player_regions[i]
            if cX >= region[0] and cX <= region[1]:
                return i+1

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

    def get_regions_of_movement(self, frame, motion_contours):
        regions = []
        for contour in motion_contours:
            # get centroid of contour
            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
            cX = int(M["m10"] / M["m00"])

            # check which region the contour is in
            for i in range (len(self.player_regions)):
                region = self.player_regions[i]
                if cX >= region[0] and cX <= region[1]:
                    regions.append(i+1)
                    break
        return regions

    def identify_movers(self, motion_contours, frame):
        moving_bodies = set()

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
                moving_bodies.add(closest_body)

        return moving_bodies


    def viz_algo(self, frame, player_images):
        movements = self.process_frame(frame)
        bodies = self.detect_bodies(frame)
        movers = self.identify_movers(movements, frame)
        self.match_faces(frame, bodies, player_images)

    def match_faces(self, frame, bodies, known_faces):
        matched_results = []
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        for (x, y, w, h) in bodies:
            # Crop upper region of the body where the face is expected
            body_roi = frame[y:y + h, x:x + w]
            face_roi = body_roi[:h // 3, :]  # Focus on the top third

            # Detect faces in the cropped region
            faces = face_cascade.detectMultiScale(face_roi, scaleFactor=1.1, minNeighbors=5)
            for (fx, fy, fw, fh) in faces:
                face_region = face_roi[fy:fy + fh, fx:fx + fw]

                # Encode the detected face
                face_encodings = face_recognition.face_encodings(face_region)
                if face_encodings:
                    face_encoding = face_encodings[0]

                    # Match with known faces
                    matches = face_recognition.compare_faces(known_faces, face_encoding)
                    distances = face_recognition.face_distance(known_faces, face_encoding)

                    # Identify the best match
                    if matches:
                        best_match_index = distances.argmin()
                        matched_name = list(known_faces.keys())[best_match_index]
                        matched_results.append({"body": (x, y, w, h), "matched_name": matched_name})

                        # Annotate the frame
                        cv2.putText(frame, matched_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return matched_results

    def match_template(self, input_frame, template_image):
        # Convert both images to grayscale
        input_gray = cv2.cvtColor(input_frame, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

        # Perform template matching
        result = cv2.matchTemplate(input_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # Find the best match location
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Define the bounding box around the detected face
        h, w = template_gray.shape
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        # Draw a rectangle around the matched region
        cv2.rectangle(input_frame, top_left, bottom_right, (0, 255, 0), 2)
        return input_frame, max_val

if __name__ == "__main__":
    motion_detector = MotionDetector()
    video = cv2.VideoCapture("IMG_0699.mov")
    # Get the total number of frames in the video
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Pick a random frame index
    random_frame_index = random.randint(0, total_frames - 1)

    # Set the video position to the random frame
    video.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)

    # Read the frame
    ret, frame = video.read()

    # Display the frame
    cv2.imshow(f"Random Frame (Index: {random_frame_index})", frame)
    cv2.waitKey(0)  # Wait for a key press to close the window

    # detect bodies in the frame
    body_frame = frame.copy()
    bodies = motion_detector.detect_bodies(frame)
    print(len(bodies))
    for (x, y, w, h) in bodies:
        cv2.rectangle(body_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow("Detected Bodies", body_frame)
    cv2.waitKey(0)

    # time how long this takes
    start = time.time()
    # check for face matches for bodies
    player_images = [face_recognition.face_encodings(face_recognition.load_image_file("adarsh.jpg")),
        face_recognition.face_encodings(face_recognition.load_image_file("amanda.jpg")),
    ]
    print("Time to load images: ", time.time() - start)

    matched_results = motion_detector.match_faces(frame, bodies, player_images)

    matched_results = motion_detector.match_faces(frame, bodies, player_images)
    for result in matched_results:
        print(result)


    # player_images = [cv2.imread("adarsh.jpg"), cv2.imread("amanda.jpg")]
    # # crop the frame to the upper third of the body
    # for (x, y, w, h) in bodies:
    #     body_roi = frame[y:y + h, x:x + w]
    #     face_roi = body_roi[:h // 4, w//4:-w//4]  # Focus on the top third
    #     cv2.imshow("Face ROI", face_roi)
    #     cv2.waitKey(0)

    # # template match the face to the known faces
    # for player_image in player_images:
    #     frame, max_val = motion_detector.match_template(frame, player_image)
    #     print(max_val)


    cv2.destroyAllWindows()

    # # Process frames from video capture
    # camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    # camera.set(cv2.CAP_PROP_FPS, 30)

    # while True:
    #     ret, frame = camera.read()
    #     if ret:
    #         # Process the frame for motion and body detection
    #         contours = motion_detector.process_frame(frame)
    #         bodies = motion_detector.detect_bodies(frame)

    #         # Create separate frames for motion contours and body detections
    #         motion_frame = frame.copy()
    #         # body_frame = frame.copy()

    #         # draw motion contours in motion frame as the contour, using draw contours
    #         for contour in contours:
    #             cv2.drawContours(motion_frame, [contour], -1, (0, 255, 0), 2)

    #         # Highlight detected bodies on body_frame
    #         for (x, y, w, h) in bodies:
    #             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    #         # Combine the two frames side by side
    #         combined_frame = np.hstack((motion_frame, frame))


    #         # Display the combined frame
    #         cv2.imshow("Motion Contours (Left) | Body Detection (Right)", combined_frame)

    #         # Break the loop if 'q' is pressed
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             break

    # Release resources
    # camera.release()
    cv2.destroyAllWindows()

