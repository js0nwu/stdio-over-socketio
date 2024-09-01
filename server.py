import os
import pty
import select
import threading
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# binary = '/notebooks/stockfish/stockfish-ubuntu-x86-64-avx2'
binary = '/notebooks/lc0/build/release/lc0'

last_input = None

@app.route('/')
def index():
    return "SocketIO server running"

@socketio.on('connect')
def handle_connect():
    print("HANDLE_CONNECT")
    # emit('response', {'data': 'Connected'})
    pass

@socketio.on('input')
def handle_input(data):
    print("HANDLE_INPUT")
    input_data = data.get('input')
    if input_data:
        global last_input
        last_input = input_data + "\r\n"
        p_out.write(last_input.encode())
        p_out.flush()

def read_binary_output():
    while True:
        try:
            ready_fds, _, _ = select.select([master_fd], [], [], 1)
            if ready_fds:
                data = os.read(master_fd, 1024)
                if data:
                    # print("===")
                    # print("data decode")
                    output_data = data.decode()
                    if last_input and output_data.startswith(last_input):
                        # print("foo starts with")
                        output_data = output_data[len(last_input + "\r\n"):]

                    # print(repr(last_input))
                    # print("<>")
                    # print(repr(output_data))
                    # print("----")
                    socketio.emit('response', {'data': output_data})
        except Exception as e:
            print(f"Error: {e}")
            if p_pid == 0:
                os.execvpe(binary, [binary], {})
            break

if __name__ == "__main__":
    p_pid, master_fd = pty.fork()
    if p_pid == 0:
        os.execvpe(binary, [binary], {})
    else:
        p_out = os.fdopen(master_fd, "w+b", 0)
        threading.Thread(target=read_binary_output, daemon=True).start()
        socketio.run(app, host="0.0.0.0", port=6006)
