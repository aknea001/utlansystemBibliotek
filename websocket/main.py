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
            event = received["event"]
            data = received["data"]

            url = "http://localhost:8000/bok/reservert"

            headers = {"Authorization": f"Bearer {received['accessToken']}"}

            if event == "nyRes":
                res = requests.post(url, json={"bokID": data["bokID"]}, headers=headers)

                if res.status_code != 200:
                    print(str(res.status_code))
                    continue

                sendDic = {
                    "event": "updRes",
                    "data": data
                }

                broadcast(connected, json.dumps(sendDic))
            elif event == "updDB":
                res = requests.post(f"{url}/update", json={"klar": data["klar"], "bokID": data["bokID"]}, headers=headers)

                if res.status_code != 200:
                    print(str(res.status_code))
                    continue
            elif event == "ping":
                await websocket.send("\n\nPong!")
    finally:
        connected.remove(websocket)

async def main():
    async with serve(handler, "", 5050):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())