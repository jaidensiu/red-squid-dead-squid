import cv2

# Load known player faces into memory (replace with actual image files)
players_info = {
    'player1': cv2.imread('player1.jpg', cv2.IMREAD_GRAYSCALE),
}

# Initialize camera
camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if not camera.isOpened():
    raise ValueError("Failed to open camera.")

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
camera.set(cv2.CAP_PROP_FPS, 30)

frame1 = None
while True:
    ret, frame2 = camera.read()
    if not ret:
        break

    cv2.imshow("Camera", frame2)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # Convert the frames to grayscale
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Initialize first frame for comparison
    if frame1 is None:
        frame1 = gray2
        continue

    # Calculate the absolute difference between frames
    frame_diff = cv2.absdiff(frame1, gray2)
    _, thresh = cv2.threshold(frame_diff, 50, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image (indicating movement)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_players = []
    for contour in contours:
        if cv2.contourArea(contour) < 500:  # Ignore small areas of motion
            continue

        # Get the bounding box of the motion region
        x, y, w, h = cv2.boundingRect(contour)
        motion_region = frame2[y:y+h, x:x+w]

        # Try to identify the player based on the motion region
        matched_player_id = None
        for player_id, player_image in players_info.items():
            res = cv2.matchTemplate(motion_region, player_image, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > 0.7:  # Threshold for considering a match
                matched_player_id = player_id
                break

        if matched_player_id:
            detected_players.append(matched_player_id)

    # Update the first frame for the next iteration
    frame1 = gray2

    print("Detected players:", detected_players)

# Cleanup
camera.release()
cv2.destroyAllWindows()