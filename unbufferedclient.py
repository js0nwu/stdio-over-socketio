#!/usr/bin/python3 -u

import socketio
import sys
import threading

# Initialize the SocketIO client
sio = socketio.Client()

# Handle connection event
@sio.event
def connect():
    # print("Connected to the server", flush=True)
    # pass
    sys.stdout.write("remote chess engine\nuciok\nreadyok\n")
    sys.stdout.flush()
    # pass


# Handle disconnection event
@sio.event
def disconnect():
    # print("Disconnected from the server", flush=True)
    pass

# Handle incoming messages from the server
@sio.on('response')
def handle_response(data):
    # Write server's output to stdout in an unbuffered manner
    sys.stdout.write(data['data'].replace("\r\n", "\n"))
    sys.stdout.flush()

def read_stdin():
    # Continuously read from stdin and send to the server
    try:
        for line in sys.stdin:
            sio.emit('input', {'input': line.strip()})
    except KeyboardInterrupt:
        pass

# Connect to the server
sio.connect('http://localhost:8889')

# Start a thread to read from stdin
stdin_thread = threading.Thread(target=read_stdin, daemon=True)
stdin_thread.start()

# Keep the client running to listen for responses
try:
    sio.wait()
except KeyboardInterrupt:
    pass
finally:
    sio.disconnect()
