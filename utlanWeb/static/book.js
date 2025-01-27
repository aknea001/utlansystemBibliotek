function display(tittel, forfatter, hylle, lant, img, elevID) {
    const backdrop = document.createElement("div")
    backdrop.classList.add("backdrop")
    backdrop.onclick = (e) => {
        if (!e.target.classList.contains("backdrop")) return;
        backdrop.remove()
    }

    const bookInfo = document.createElement("div")
    bookInfo.classList.add("popup-window")
    bookInfo.innerHTML = `
        <button class="popup-close" onclick="closePopup()">×</button>
        <div class="popup-title">${tittel}</div>
        <div class="popup-author">av ${forfatter}</div>
        <img src="/static/covers/${img}" alt="Book Cover" class="popup-image"><br>
    `

    if (lant != "None") {
        bookInfo.innerHTML += `
        <div class="popup-status lent">Lånt</div>`
    } else {
        bookInfo.innerHTML += `
        <div class="popup-shelf">Hylle: ${hylle}</div>
        <div class="popup-status available">Tilgjengelig</div>
        <br><button onclick="nyRes(${elevID}, '${tittel}', '${forfatter}', '${hylle}')" class="popup-status reserver">Reserver</button>`
    }

    document.body.appendChild(backdrop)
    backdrop.appendChild(bookInfo)
}

function closePopup() {
    const backdrop = document.querySelector(".backdrop")
    backdrop.remove()
}

function websocketConnect() {
    const socket = io('http://localhost:5050')
    socket.on("connected", data => {
        console.log(data.message)
    })

    return socket
}

function nyRes(elevID, tittel, forfatter, hylle) {
    if (!elevID) {
        window.location = "/login"
        return
    }

    const socket = websocketConnect()

    socket.emit("nyRes", {bokTittel: tittel, bokForfatter: forfatter, bokHylle: hylle}, () => {
        socket.disconnect()
        location.reload()
    })
}