from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("connect")
def connect():
    print("New client connected")
    emit("connected", {"message": "Connected to webSocket"})

@socketio.on("nyRes")
def nyRes(data):
    print(data)
    emit("updateRes", {"info": data}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5050)