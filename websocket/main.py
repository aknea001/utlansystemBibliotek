from flask import Flask
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("connect")
def connect():
    print("New client connected")
    emit("connected", {"message": "Connected to webSocket"})

@socketio.on("nyRes")
def nyRes(data):
    print(data)

    url = f"http://localhost:8000/bok/{data["bokID"]}"

    res = requests.post(url, json={"elevID": data["elevID"], "dager": 2})

    if res.status_code != 200:
        return res.status_code
    
    emit("updateRes", {"info": data}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5050)