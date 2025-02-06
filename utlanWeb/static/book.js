function redirect(e, page=null, newPage=null) {
    e.preventDefault()
    const currentLoc = new URL(window.location.href)

    if (!page) {
        const searchInput = document.getElementById("searchQuery")

        if (searchInput.value == "") {
            currentLoc.searchParams.set("page", 1)
            currentLoc.searchParams.delete("search")
        } else {
            currentLoc.searchParams.set("page", 1)
            currentLoc.searchParams.set("search", searchInput.value)
        }
    } else if (newPage > 0) {
        currentLoc.searchParams.set("page", parseInt(page) + 1)
    } else {
        currentLoc.searchParams.set("page", parseInt(page) - 1)
    }

    window.location = currentLoc
}

function display(tittel, forfatter, hylle, lant, img, bokID, accessToken) {
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
    } else 
        bookInfo.innerHTML += `
        <div class="popup-shelf">Hylle: ${hylle}</div>
        <div class="popup-status available">Tilgjengelig</div>
        <br><button onclick="nyRes('${accessToken}', ${bokID}, '${tittel}', '${forfatter}', '${hylle}')" class="popup-status reserver">Reserver</button>`
    

    document.body.appendChild(backdrop)
    backdrop.appendChild(bookInfo)
}

function closePopup() {
    const backdrop = document.querySelector(".backdrop")
    backdrop.remove()
}

function nyRes(accessToken, bokID, tittel, forfatter, hylle) {
    const xhr = new XMLHttpRequest()

    xhr.open("GET", "http://localhost:8000/validateJWT")
    xhr.setRequestHeader("Authorization", `Bearer ${accessToken}`)
    xhr.send()
    xhr.responseType = "json"
    xhr.onload = () => {
        if (xhr.status != 200) {
            window.location = "/login"
        }
    }

    if (!accessToken) {
        window.location = "/login"
        return
    }

    const websocket = new WebSocket("ws://localhost:5050")

    websocket.addEventListener("open", () => {
        const payload = {
            "event": "nyRes",
            "accessToken": accessToken,
            "data": {
                "bokID": bokID,
                "tittel": tittel,
                "forfatter": forfatter,
                "hylle": hylle
            }
        }

        websocket.send(JSON.stringify(payload))
    })

    websocket.addEventListener("message", ({ data }) => {
        const rawdata = JSON.parse(data)

        if (rawdata.event == "updRes") {
            websocket.close()
            location.reload()
        }
    })
}