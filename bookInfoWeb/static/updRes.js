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

    li.innerHTML = `<b>${WSdata.tittel}</b> av ${WSdata.forfatter}, ${WSdata.hylle}
    <button onclick="accept(this)">✓</button>  <button onclick="decline(this)">✘</button>`
    li.setAttribute("wsData", JSON.stringify(WSdata))
    notifs.appendChild(li)
})

function accept(element, accessToken) {
    const Lparent = element.parentElement

    const rawdata = JSON.parse(Lparent.getAttribute("wsData"))

    console.log(rawdata)

    const payload = {
        "event": "updDB",
        "accessToken": accessToken,
        "data": {
            "klar": true,
            "bokID": rawdata.bokID
        }
    }

    websocket.send(JSON.stringify(payload))

    Lparent.remove()
}

function decline(element, accessToken) {
    const Lparent = element.parentElement

    const rawdata = JSON.parse(Lparent.getAttribute("wsData"))

    const payload = {
        "event": "updDB",
        "accessToken": accessToken,
        "data": {
            "klar": false,
            "bokID": rawdata.bokID
        }
    }

    websocket.send(JSON.stringify(payload))

    Lparent.remove()
}