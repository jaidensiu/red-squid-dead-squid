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
BACKEND_PORT = os.environ['BACKEND_PORT']
RPI_SERVER_URL = f"ws://{RPI_IP}:{BACKEND_PORT}"
game_in_progress = False
players_info = {}  # A dictionary that stores player information (e.g., images of the players)

# List to store eliminated players (by player ID or other unique identifiers)
eliminated_players = []

# Flag to track if video frames are currently being processed
is_streaming = False
last_frame_time = time.time()

async def send_eliminated_players(ws):
    """
    Send eliminated players to the Raspberry Pi only once when video stream stops.
    """
    global eliminated_players

    if eliminated_players:
        data = {"type": "eliminated_players", "payload": eliminated_players}
        await ws.send(json.dumps(data))
        logging.info(f"Sent eliminated players: {eliminated_players}")
        eliminated_players.clear()

async def detect_motion_and_identify_players(frame1, frame2):
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

    return detected_players

async def backend_client(ws):
    global is_streaming, last_frame_time, players_info, eliminated_players

    previous_frame = None
    while True:
        try:
            message = await ws.recv()
            data = json.loads(message)

            if data.get("type") == "frame":
                # Handle frame data
                # Base64 decode the frame data
                frame_data = base64.b64decode(data["payload"])
                frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                cv2.imshow("Frame", frame)
                cv2.waitKey(1)

                # Track the time of the last frame
                current_time = time.time()
                if current_time - last_frame_time > 10:
                    if is_streaming:
                        logging.info(f"Video stream stopped, sending eliminated players...")
                        await send_eliminated_players(ws)
                        is_streaming = False
                    last_frame_time = current_time

                else:
                    if previous_frame is not None:
                        detected_players = await detect_motion_and_identify_players(previous_frame, frame)
                        if detected_players:
                            logging.info(f"Motion detected for players: {detected_players}")
                            for player_id in detected_players:
                                if player_id not in eliminated_players:
                                    eliminated_players.append(player_id)
                                    logging.info(f"Player {player_id} eliminated.")

                    is_streaming = True
                    last_frame_time = current_time

                previous_frame = frame

            elif data.get("type") == "player_info":
                # Handle player image data
                for player_id, player_image_data in data.get("payload", {}).items():
                    # Base64 decode the player image data
                    player_image_data_decoded = base64.b64decode(player_image_data)
                    player_image_array = np.frombuffer(player_image_data_decoded, dtype=np.uint8)
                    player_image = cv2.imdecode(player_image_array, cv2.IMREAD_GRAYSCALE)
                    players_info[player_id] = player_image
                    logging.info(f"Loaded image for player {player_id}")

        except websockets.exceptions.ConnectionClosedError as e:
            logging.info(f"WebSocket connection closed: {e}")
            break
        except websockets.exceptions.ConnectionClosedOK:
            logging.info("WebSocket connection closed normally.")
            break
        except Exception as e:
            logging.info(f"Unexpected error: {e}")
            break


async def main():
    async with websockets.connect(RPI_SERVER_URL) as ws:
        logging.info(f"Connected to WebSocket server at {RPI_SERVER_URL}")
        await backend_client(ws)

asyncio.run(main())
