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
    notifs.appendChild(li)
})

function accept(element) {
    //api post request 

    (element.parentElement).remove()
}

function decline(element) {
    //api post request 

    (element.parentElement).remove()
}