function display(tittel, forfatter, hylle, img) {
    const backdrop = document.createElement("div")
    backdrop.classList.add("backdrop")
    backdrop.onclick = (e) => {
        if (!e.target.classList.contains("backdrop")) return;
        backdrop.remove()
    }

    const bookInfo = document.createElement("div")
    bookInfo.classList.add("bookInfo")
    bookInfo.innerHTML = `
        <p>${tittel} av ${forfatter}</p>
        <img style="height: 500px; width: 350px;" src="/static/${img}" alt="">
        <p>Hylle: ${hylle}</p>
    `

    document.body.appendChild(backdrop)
    backdrop.appendChild(bookInfo)
}