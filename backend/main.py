import asyncio
import websockets
import cv2
import numpy as np
import json
import time
import os
import logging
from vision import MotionDetector
import base64
import dotenv
dotenv.load_dotenv()

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

# Global constants
RPI_IP = os.environ['RPI_IP']
EVIN_IP = os.environ['EVIN_IP']
CURRENT_IP = RPI_IP
BACKEND_PORT = os.environ['BACKEND_PORT']
CURRENT_SERVER_URL = f"ws://{CURRENT_IP}:{BACKEND_PORT}"
MAX_NUM_PLAYERS = 4

# Global variables
game_in_progress = False
players_info = [None] * 5
num_players = 0
all_eliminated_players = set() # A list to track eliminated players
is_streaming = False # Flag to track if video frames are currently being processed

# Initialize motion detector and player identifier
motion_detector = MotionDetector()

async def send_eliminated_players(ws, eliminated_players):
    # There is already a check making sure newly eliminated players have not been eliminated before
    if eliminated_players is not None:
        await ws.send(json.dumps({"type": "eliminated_players", "data": list(eliminated_players)}))
        logging.info(f"Sent eliminated players: {eliminated_players}")

    # Update the list of all eliminated players
    all_eliminated_players.update(eliminated_players)

async def backend_client(ws):
    global is_streaming, players_info, num_players, all_eliminated_players
    eliminated_players = list()

    # Output video file, mp4 format
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('cv/output.mp4', fourcc, 20.0, (960, 540))

    while True:
        try:
            message = await ws.recv()
            packet = json.loads(message)

            if packet.get("type") == "players_info":
                logging.info("Received players info")
                num_players = len(packet.get("data", list()))

                for player_id, player_image_data in enumerate(packet.get("data", list())):
                    # Base64 decode the player image data
                    player_id += 1  # Player IDs are 1-indexed
                    player_image_data_decoded = base64.b64decode(player_image_data)
                    with open(f"player_images/{player_id}.jpg", "wb") as f:
                        f.write(player_image_data_decoded)

                    player_image_array = np.frombuffer(player_image_data_decoded, dtype=np.uint8)
                    player_image = cv2.imdecode(player_image_array, cv2.IMREAD_COLOR)
                    players_info[player_id] = player_image
                    logging.info(f"Loaded image for player {player_id}")

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
                    is_streaming = False
                    cv2.destroyAllWindows()  # Ensures all OpenCV windows are closed at this point

            elif packet.get("type") == "video_frame":
                if is_streaming:
                    # Handle frame data
                    frame_data = base64.b64decode(packet.get("data"))
                    frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

                    motion_contours = motion_detector.process_frame(frame)
                    body_detections = motion_detector.detect_bodies(frame)

                    body_frame = frame.copy()
                    motion_frame = frame.copy()

                    # for contour in motion_contours:
                    #     (x, y, w, h) = cv2.boundingRect(contour)
                    #     cv2.rectangle(motion_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    for contour in motion_contours:
                        cv2.drawContours(motion_frame, [contour], -1, (0, 255, 0), 2)

                    for body in body_detections:
                        (x, y, w, h) = body
                        cv2.rectangle(body_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                    combined_frame = np.hstack((motion_frame, body_frame))

                    # Show the frame with motion contours, show a smaller cv2 window
                    cv2.imshow("Motion and Body", combined_frame)
                    out.write(frame)
                    cv2.waitKey(1)

                    # detected_players = await identify_players(motion_contours, frame)
                    detected_players = [1, 2, 3]  # Dummy dat
                    for player_id in detected_players:
                        if player_id not in all_eliminated_players and player_id <= num_players:
                            eliminated_players.append(player_id)
                            all_eliminated_players.add(player_id)
                            logging.info(f"Player {player_id} eliminated")


        except websockets.exceptions.ConnectionClosedError as e:
            logging.info(f"WebSocket connection closed: {e}")
            break
        except websockets.exceptions.ConnectionClosedOK:
            logging.info("WebSocket connection closed normally")
            break
        except Exception as e:
            logging.info(f"Unexpected error: {e}")
            break
        finally:
            out.release()
            cv2.destroyAllWindows()

async def main():
    async with websockets.connect(CURRENT_SERVER_URL) as ws:
        logging.info(f"Connected to WebSocket server at {CURRENT_SERVER_URL}")
        await backend_client(ws)

asyncio.run(main())
