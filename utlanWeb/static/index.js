const nameInput = document.getElementById("navn")
const dataList = document.getElementById("dataL")
const xhr = new XMLHttpRequest()

function APIcall(searchQuery, fornavn, callback) {
    xhr.open("GET", "http://localhost:8000/elevNavn")
    xhr.setRequestHeader("searchQuery", searchQuery)
    if (fornavn) {
        xhr.setRequestHeader("fornavn", fornavn)
    }
    xhr.send()
    xhr.responseType = "json"
    xhr.onload = () => {
        if (xhr.readyState == 4 && xhr.status == 200) {
            callback(xhr.response)
        } else {
            console.log(xhr.status)
        }
    }
}

let oldValue

function search() {
    const fullQuery = nameInput.value
    let nameValue = nameInput.value
    let fornavn = null
    
    if (nameValue != (null || "") && nameValue != oldValue) {
        dataList.innerHTML = ""

        if (nameValue.includes(" ")) {
            const nameLst = [nameValue.substring(0, nameValue.indexOf(" ")), nameValue.substring(nameValue.indexOf(" ") + 1)]
            nameValue = nameLst[1]
            fornavn = nameLst[0]
        }

        APIcall(nameValue, fornavn, (data) => {
            for (i=0; i<data.length; i++) {
                const str = `${String(data[i][0])} ${String(data[i][1])}`
     
                const option = document.createElement("option")
                option.value = str

                dataList.appendChild(option)
            }
        })

        oldValue = fullQuery
    } else if (nameValue == (null || "")) {
        dataList.innerHTML = ""
        oldValue = null
    }

    setTimeout(search, 200)
}

search()