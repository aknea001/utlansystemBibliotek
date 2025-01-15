const nameInput = document.getElementById("navn")
const dataList = document.getElementById("dataL")
const xhr = new XMLHttpRequest()

function APIcall(searchQuery, callback) {
    xhr.open("GET", "http://localhost:8000/elevNavn")
    xhr.setRequestHeader("searchQuery", searchQuery)
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
    const nameValue = nameInput.value
    
    if (nameValue != (null || "") && nameValue != oldValue) {
        dataList.innerHTML = ""
        
        APIcall(nameValue, (data) => {
            for (i=0; i<data.length; i++) {
                const str = `${String(data[i][0])} ${String(data[i][1])}`
     
                const option = document.createElement("option")
                option.value = str

                dataList.appendChild(option)
            }
        })

        oldValue = nameValue
    } else if (nameValue == (null || "")) {
        dataList.innerHTML = ""
        oldValue = null
    }

    setTimeout(search, 200)
}

search()