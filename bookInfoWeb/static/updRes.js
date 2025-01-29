const websocket = new WebSocket("ws://localhost:5050")

websocket.addEventListener("open", () => {
    console.log("connected to websocket..")
})

websocket.addEventListener("message", ({ data }) => {
    const received = JSON.parse(data)
    const WSdata = received.data

    console.log(WSdata)

    const notifs = document.getElementById("notifs")
    const li = document.createElement("li")

    li.innerHTML = `<b>${WSdata.tittel}</b> av ${WSdata.forfatter}, ${WSdata.hylle} - ${WSdata.elevID}
    <button onclick="accept(this)">✓</button>  <button onclick="decline(this)">✘</button>`
    li.setAttribute("wsData", data)
    notifs.appendChild(li)
})

function accept(element) {
    const Lparent = element.parentElement

    data = JSON.parse(Lparent.getAttribute("wsData"))

    const payload = {
        "event": "updDB",
        "data": {
            "reservert": true,
            "bokID": data.bokID
        }
    }

    websocket.send(JSON.stringify(payload))

    Lparent.remove()
}

function decline(element, data) {
    const payload = {
        "event": "updDB",
        "data": {
            "reservert": false,
            "bokID": JSON.parse(data).bokID
        }
    }

    websocket.send(JSON.stringify(payload))

    (element.parentElement).remove()
}