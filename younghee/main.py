import asyncio
import websockets
import cv2
import json
import time
import os
import logging
import random
import base64
from audio import Audio
from servo import Servo
from camera import Camera
from dotenv import load_dotenv
load_dotenv()

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

# Global constants
RPI_IP = os.environ['RPI_IP']
EVIN_IP = os.environ['EVIN_IP']
CURRENT_IP = EVIN_IP
BACKEND_PORT = os.environ['BACKEND_PORT']
MOBILE_APP_PORT = os.environ['MOBILE_APP_PORT']
MAX_GAME_TIME = 180  # 3 minutes
COUNTDOWN_TIME = 5  # 5 seconds
MAX_PLAYERS = 4

# Global variables
game_in_progress = False
num_players = 0
mobile_app_socket = None
backend_socket = None
eliminated_players_event = asyncio.Event()  # Event to signal when eliminated players are received
all_eliminated_players = set()  # List to track eliminated players

# Initialize the audio player, servo controller, and camera
audio = Audio()   # Initialize the audio player
servo = Servo()  # Initialize the servo controller
camera = Camera()  # Initialize the camera

async def mobile_app_handler(websocket):
    logging.info(f"Mobile app connected: {websocket.remote_address}")

    global mobile_app_socket, backend_socket, game_in_progress, num_players
    mobile_app_socket = websocket

    async for message in websocket:
        packet = json.loads(message)
        if packet.get("type") == "players_info":
            if not game_in_progress:
                game_in_progress = True  # Set the game to in-progress when player info is received
                num_players = len(packet.get("data", list()))
                # Display the player images as a list
                for player_id, player_image in enumerate(packet.get("data", list())):
                    player_id += 1 # Player IDs are 1-indexed
                    with open(f"player_images/{player_id}.jpg", "wb") as f:
                        f.write(base64.b64decode(player_image))

                logging.info(f"Received players info, total players: {num_players}")
                logging.info(f"Setting game in progress to: {game_in_progress}")

                # Echo the players info to the backend client
                if backend_socket:
                    await backend_socket.send(message)
                    logging.info(f"Echoed players info to backend")
            else:
                logging.warning("Game is already in progress, ignoring players info")

async def backend_handler(websocket):
    logging.info(f"Backend connected: {websocket.remote_address}")

    global backend_socket, mobile_app_socket, all_eliminated_players
    backend_socket = websocket

    async for message in websocket:
        packet = json.loads(message)
        if packet.get("type") == "eliminated_players":
            eliminated_players = packet.get("data", list())
            all_eliminated_players.update(eliminated_players)
            logging.info(f"Received eliminated players: {eliminated_players}")
            logging.info(f"Total eliminated players: {all_eliminated_players}")

            # Echo eliminated players data to the mobile app
            if mobile_app_socket:
                await mobile_app_socket.send(message)
                logging.info("Echoed eliminated players to mobile app")

            # Play the elimination audio
            logging.info("Playing elimination audio...")
            audio.play_audio("elimination.wav")
            for player_id in eliminated_players:
                audio.play_audio(f"player_{player_id}.wav")

            # Set the event to signal the game loop to proceed
            eliminated_players_event.set()
            logging.info("Set eliminated players event")

async def main_game_loop():
    global backend_socket, mobile_app_socket, game_in_progress, num_players, eliminated_players_event, all_eliminated_players

    try:
        while True:
            if game_in_progress:
                # 1. Start game
                logging.info("Game is now starting...")
                start_time = time.time()
                end_time = int(start_time + MAX_GAME_TIME + COUNTDOWN_TIME)
                if mobile_app_socket:
                    logging.info(f"Sending game end time {end_time} to mobile app")
                    await mobile_app_socket.send(json.dumps({"type": "game_end_time", "data": int(end_time)}))
                await asyncio.sleep(COUNTDOWN_TIME + 2)  # Wait for the mobile app to receive the game end time

                while True:
                    # 2. Green light and random wait time
                    servo.turn_backwards()
                    await asyncio.sleep(1) # For dramatic effect
                    audio.play_audio("green_light.wav")
                    wait_time = random.uniform(1, 1.75)
                    logging.info(f"Waiting for {wait_time} seconds...")
                    await asyncio.sleep(wait_time)

                    # 3. Red light, turn head around
                    light_number = random.randint(1, 2)
                    audio.play_audio_without_wait(f"red_light_{light_number}.wav")
                    servo.turn_forwards()

                    # 4. Start capturing video for 10 seconds at 30 FPS
                    if backend_socket:
                        logging.info("Sending start video stream command to backend")
                        await backend_socket.send(json.dumps({"type": "start_video_stream", "data": bool(True)}))

                    logging.info("Capturing video and sending to backend...")
                    time_end = time.time() + 5  # Capture for 5 seconds
                    while time.time() < time_end:
                        encoded_buffer = camera.capture_and_encode_image()
                        if encoded_buffer is not None:
                            if backend_socket:
                                await backend_socket.send(json.dumps({"type": "video_frame", "data": str(encoded_buffer)}))

                    if backend_socket:
                        logging.info("Sending stop video stream command to backend")
                        await backend_socket.send(json.dumps({"type": "stop_video_stream", "data": bool(True)}))

                    # 5. Wait until the eliminated players are sent back to us before proceeding
                    logging.info("Waiting for eliminated players...")
                    await eliminated_players_event.wait()
                    logging.info("Eliminated players received")
                    eliminated_players_event.clear()

                    # 6. Check for game end conditions (either no players left or max game time reached)
                    if len(all_eliminated_players) >= num_players or (time.time() - start_time) > MAX_GAME_TIME:
                        logging.info("Game has ended due to no players left or max game time reached")
                        if mobile_app_socket:
                            logging.info("Sending game over signal to mobile app")
                            await mobile_app_socket.send(json.dumps({"type": "game_over", "data": bool(True)}))

                        logging.info("Playing game end audio...")
                        audio.play_audio("game_end.wav")
                        game_in_progress = False
                        break

            else:
                await asyncio.sleep(1)  # Idle when the game is not active
    finally:
        await camera.close()

async def main():
    # Start WebSocket servers for mobile app and backend
    logging.info(f"WebSocket server for mobile app started on ws://{CURRENT_IP}:{MOBILE_APP_PORT}")
    logging.info(f"WebSocket server for backend client started on ws://{CURRENT_IP}:{BACKEND_PORT}")

    await asyncio.gather(
        websockets.serve(mobile_app_handler, CURRENT_IP, MOBILE_APP_PORT),
        websockets.serve(backend_handler, CURRENT_IP, BACKEND_PORT),
        main_game_loop()
    )

asyncio.run(main())
