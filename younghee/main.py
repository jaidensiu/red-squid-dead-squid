import asyncio
import websockets
import cv2
import json
import time
import os
import base64
import logging
import pygame
from audio import Audio
from servo import Servo
from dotenv import load_dotenv
load_dotenv()

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,  # Set the logging level
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
                    datefmt='%Y-%m-%d %H:%M:%S')  # Date format for the log timestamp

# Set up global variables
RPI_IP = os.environ['RPI_IP']
BACKEND_PORT = os.environ['BACKEND_PORT']
MOBILE_APP_PORT = os.environ['MOBILE_APP_PORT']
game_in_progress = False
mobile_app_socket = None
backend_socket = None
eliminated_players_event = asyncio.Event()  # Event to signal when eliminated players are received
eliminated_players = []  # List to track eliminated players

audio = Audio()  # Initialize the audio player
servo = Servo()  # Initialize the servo controller

async def mobile_app_handler(websocket):
    logging.info(f"Mobile app connected: {websocket.remote_address}")

    global mobile_app_socket
    global game_in_progress
    mobile_app_socket = websocket

    async for message in websocket:
        data = json.loads(message)
        if data.get("type") == "game_status":
            game_in_progress = data.get("payload", False)
        elif data.get("type") == "player_info":
            if not game_in_progress:
                logging.info("Game not in progress. Player info not processed.")
            else:
                # Forward to the backend
                if backend_socket:
                    await backend_socket.send(json.dumps({"type": "player_info", "payload": data.get("payload")}))

        await websocket.send(json.dumps({"status": "success"}))

async def backend_handler(websocket):
    logging.info(f"Backend connected: {websocket.remote_address}")

    global backend_socket
    global eliminated_players
    backend_socket = websocket

    async for message in websocket:
        data = json.loads(message)
        if data.get("type") == "eliminated_players":
            # Access the payload (list of eliminated players)
            eliminated_players = data.get("payload", [])
            logging.info(f"Received eliminated players: {eliminated_players}")

            # Send the eliminated players data to the mobile app
            if mobile_app_socket:
                await mobile_app_socket.send(json.dumps({"type": "eliminated_players", "payload": eliminated_players}))

            # Set the event to signal the game loop to proceed
            eliminated_players_event.set()

            # Play audio or trigger other actions here (e.g., playing doll audio)
            logging.info("Playing doll audio...")
            # play_audio("doll_audio.mp3")


async def main_game_loop():
    global backend_socket
    global game_in_progress
    global eliminated_players_event
    global eliminated_players

    cap = cv2.VideoCapture(0)  # Camera capture
    max_game_time = 60  # Example game time limit in seconds
    start_time = time.time()  # Start time of the game

    try:
        while True:
            if game_in_progress:
                # 1. Do countdown (could be added here, for example, use time for countdown)
                logging.info("Starting countdown...")
                await asyncio.sleep(3)

                # 2. Start game (game starts after countdown)
                logging.info("Game started!")

                # 3. Play doll audio (trigger audio playback here)
                logging.info("Playing doll audio...")
                sound = pygame.mixer.Sound("singing.wav")
                sound.play()
                pygame.time.wait(int(sound.get_length() * 1000))  # Wait for the sound to finish

                await asyncio.sleep(5)  # Simulate audio playback time

                # 4. Turn head around (servo control or other actions)
                logging.info("Turning head around...")
                await asyncio.sleep(2)

                # 5. Start capturing video for 10 seconds at 30 FPS
                logging.info("Capturing video...")
                time_end = time.time() + 10  # Capture for 10 seconds
                while time.time() < time_end:
                    ret, frame = cap.read()
                    if ret:
                        _, buffer = cv2.imencode(".jpg", frame)
                        encoded_buffer = base64.b64encode(buffer.tobytes()).decode('utf-8')  # Base64 encode bytes to string

                        # Sending the base64-encoded frame as part of the JSON payload
                        if backend_socket:
                            await backend_socket.send(json.dumps({"type": "frame", "payload": encoded_buffer}))
                    else:
                        logging.info("Error capturing frame")

                    await asyncio.sleep(0.033)  # 30 FPS

                # 6. Wait until the eliminated players are sent back to us before proceeding
                logging.info("Waiting for eliminated players...")
                await eliminated_players_event.wait()

                # 7. Once the event is set, clear it and proceed to the next round
                eliminated_players_event.clear()

                # 8. Check for game end conditions (either no players left or max game time reached)
                if len(eliminated_players) >= 10 or (time.time() - start_time) > max_game_time:
                    logging.info("Game Over!")
                    break  # Exit the loop if game is over (either no players left or timer ran out)

            else:
                logging.info("Game not in progress")
                await asyncio.sleep(1)  # Idle when the game is not active

    finally:
        cap.release()

async def main():
    # Start WebSocket servers for mobile app and backend
    logging.info(f"WebSocket server for mobile app started on ws://{RPI_IP}:{MOBILE_APP_PORT}")
    logging.info(f"WebSocket server for backend client started on ws://{RPI_IP}:{BACKEND_PORT}")

    await asyncio.gather(
        websockets.serve(mobile_app_handler, RPI_IP, MOBILE_APP_PORT),
        websockets.serve(backend_handler, RPI_IP, BACKEND_PORT),
        main_game_loop()
    )

asyncio.run(main())