import asyncio
import websockets
import cv2
import numpy as np
import json
import time
import os
import logging
import base64
import dotenv
dotenv.load_dotenv()

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

RPI_IP = os.environ['RPI_IP']
EVIN_IP = os.environ['EVIN_IP']
CURRENT_IP = EVIN_IP
BACKEND_PORT = os.environ['BACKEND_PORT']
CURRENT_SERVER_URL = f"ws://{CURRENT_IP}:{BACKEND_PORT}"

game_in_progress = False
players_info = [None] * 5
all_eliminated_players = set() # A list to track eliminated players
is_streaming = False # Flag to track if video frames are currently being processed

async def send_eliminated_players(ws, eliminated_players):
    # There is already a check making sure newly eliminated players have not been eliminated before
    if eliminated_players:
        await ws.send(json.dumps({"type": "eliminated_players", "data": list(eliminated_players)}))
        logging.info(f"Sent eliminated players: {eliminated_players}")
        eliminated_players.clear()

    # Update the list of all eliminated players
    all_eliminated_players.update(eliminated_players)

async def identify_players(motion_contours, frame):
    global players_info
    detected_players = []
    pass

async def detect_motion(frame1, frame2):
    """
    Detect motion between two frames and identify the players based on motion.
    """
    # Convert frames to grayscale
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Calculate the absolute difference between frames
    frame_diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(frame_diff, 50, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image (indicating movement)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 500:  # Ignore small areas of motion
            continue

        # Get the bounding box of the motion region
        x, y, w, h = cv2.boundingRect(contour)
        motion_region = frame2[y:y+h, x:x+w]

        # # Try to identify the player based on the motion region
        # matched_player_id = None
        # for player_id, player_image in players_info.items():
        #     res = cv2.matchTemplate(motion_region, player_image, cv2.TM_CCOEFF_NORMED)
        #     _, max_val, _, _ = cv2.minMaxLoc(res)

        #     if max_val > 0.7:  # Threshold for considering a match
        #         matched_player_id = player_id
        #         break

        # if matched_player_id:
        #     detected_players.append(matched_player_id)

    # return detected_players
    return []

async def backend_client(ws):
    global is_streaming, players_info, all_eliminated_players
    previous_frame = None
    eliminated_players = list()

    while True:
        try:
            message = await ws.recv()
            packet = json.loads(message)

            if packet.get("type") == "players_info":
                # Handle player image data
                for player_id, player_image_data in enumerate(packet.get("data", list())):
                    # Base64 decode the player image data
                    player_id += 1  # Player IDs are 1-indexed
                    player_image_data_decoded = base64.b64decode(player_image_data)
                    player_image_array = np.frombuffer(player_image_data_decoded, dtype=np.uint8)
                    player_image = cv2.imdecode(player_image_array, cv2.IMREAD_COLOR)
                    players_info[player_id] = player_image
                    logging.info(f"Loaded image for player {player_id}")
                    cv2.imshow(f"Player {player_id}", player_image)
                    cv2.waitKey(5000) # Display the image for 3 seconds

            elif packet.get("type") == "start_video_stream":
                logging.info("Received start video stream command")
                eliminated_players.clear() # Just in case
                previous_frame = None # Just in case
                is_streaming = True

            elif packet.get("type") == "stop_video_stream":
                logging.info("Received stop video stream command")
                if is_streaming:
                    logging.info(f"Video stream stopped, sending eliminated players...")
                    await send_eliminated_players(ws, eliminated_players)
                    eliminated_players.clear()
                    previous_frame = None
                    is_streaming = False

            elif packet.get("type") == "video_frame":
                if is_streaming:
                    # Handle frame data
                    frame_data = base64.b64decode(packet.get("data"))
                    frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                    cv2.imshow("RPI video stream", frame)
                    cv2.waitKey(1)

                    if previous_frame is not None:
                        motion_contours = await detect_motion(previous_frame, frame)
                        detected_players = await identify_players(motion_contours, frame)
                        for player_id in detected_players:
                            if player_id not in all_eliminated_players:
                                eliminated_players.add(player_id)
                                logging.info(f"Player {player_id} eliminated")

                    previous_frame = frame

        except websockets.exceptions.ConnectionClosedError as e:
            logging.info(f"WebSocket connection closed: {e}")
            break
        except websockets.exceptions.ConnectionClosedOK:
            logging.info("WebSocket connection closed normally")
            break
        except Exception as e:
            logging.info(f"Unexpected error: {e}")
            break

async def main():
    async with websockets.connect(CURRENT_SERVER_URL) as ws:
        logging.info(f"Connected to WebSocket server at {CURRENT_SERVER_URL}")
        await backend_client(ws)

asyncio.run(main())
