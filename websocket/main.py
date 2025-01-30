import asyncio
import json
import requests
from websockets.asyncio.server import broadcast, serve

connected = set()

async def handler(websocket):
    connected.add(websocket)

    try:
        async for msg in websocket:
            received = json.loads(msg)

            print(received)

            assert "event" in received

            if received["event"] == "nyRes":
                data = received["data"]

                url = f"http://localhost:8000/bok/{data["bokID"]}"

                res = requests.post(url, json={"elevID": data["elevID"], "dager": 2})

                if res.status_code != 200:
                    print(str(res.status_code))
                    continue

                sendDic = {
                    "event": "updRes",
                    "data": data
                }

                broadcast(connected, json.dumps(sendDic))
            elif received["event"] == "ping":
                await websocket.send("\n\nPong!")
    finally:
        connected.remove(websocket)

async def main():
    async with serve(handler, "", 5050):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())