function display(tittel, forfatter, hylle, lant, img) {
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
        <img src="/static/${img}" alt="Book Cover" class="popup-image"><br>
    `

    if (lant != "None") {
        bookInfo.innerHTML += `
        <div class="popup-status lent">Lånt</div>`
    } else {
        bookInfo.innerHTML += `
        <div class="popup-status available">Tilgjengelig</div>
        <div class="popup-shelf">Hylle: ${hylle}</div>`
    }

    document.body.appendChild(backdrop)
    backdrop.appendChild(bookInfo)
}

function closePopup() {
    const backdrop = document.querySelector(".backdrop")
    backdrop.remove()
}