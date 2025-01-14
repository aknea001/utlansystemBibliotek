const nameInput = document.getElementById("navn")
const outputField = document.getElementById("output")
const xhr = new XMLHttpRequest()

function APIcall(searchQuery, callback) {
    xhr.open("GET", "http://localhost:8000/elevNavn")
    xhr.setRequestHeader("searchQuery", searchQuery)
    xhr.send()
    xhr.responseType = "json"
    xhr.onload = () => {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log(xhr.response)
            callback(xhr.response)
        } else {
            console.log(xhr.status)
        }
    }
}

let oldValue

function test() {
    const nameValue = nameInput.value
    
    if (nameValue != (null || "") && nameValue != oldValue) {
        console.log(nameValue)
        outputField.innerText = ""
        
        APIcall(nameValue, (data) => {
            for (i=0; i<data.length; i++) {
                const str = `${String(data[i][0])} ${String(data[i][1])}\n`
    
                outputField.innerText += str
            }
        })

        oldValue = nameValue
    } else if (nameValue == (null || "")) {
        outputField.innerText = ""
        oldValue = null
    }

    setTimeout(test, 200)
}

test()