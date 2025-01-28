const websocket = new WebSocket("ws://localhost:5050")

websocket.addEventListener("message", ({ data }) => {
    const received = JSON.parse(data)

    console.log(received.data)
})