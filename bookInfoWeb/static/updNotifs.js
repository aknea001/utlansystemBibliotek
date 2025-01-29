const websocket = new WebSocket("ws://localhost:5050")

websocket.addEventListener("open", () => {
    console.log("Connected to websocket...")
})

websocket.addEventListener("message", ({ data }) => {
    const rawdata = JSON.parse(data)

    newNotif(rawdata.data.tittel)
})

function newNotif(title) {
    const notifContainer = document.querySelector(".notifications-container")
    const notif = document.createElement("a")

    notif.classList.add("notification")
    notif.innerHTML = `
    <p>Ny reservation</p>
    <p>${title}</p>`

    notif.setAttribute("href", "/reservert")

    notifContainer.appendChild(notif)
}