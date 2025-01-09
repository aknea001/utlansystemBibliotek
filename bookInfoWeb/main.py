from flask import Flask, render_template, session, request, redirect, url_for
from dotenv import load_dotenv
from os import getenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("FLASKPASSWD")

@app.route("/<bokID>", methods=["GET", "POST"])
def index(bokID):
    url = f"http://localhost:8000/bok/{bokID}"

    if request.method == "GET":
        response = requests.get(url)

        if response.status_code == 200:
            responseJson = response.json()
            bokInfo = responseJson["bokInfo"]
            elevInfo = responseJson["elevInfo"]

            navn = bokInfo["navn"]
            forfatter = bokInfo["forfatter"]
            sjanger = bokInfo["sjanger"]
            hylle = bokInfo["hylle"]

            elevNavn = f"{elevInfo['navn']['first']} {elevInfo['navn']['last']}"
            programfag = elevInfo["programfag"]

            if responseJson["leid"]:
                session["leid"] = True
            else:
                session.clear()

            return render_template("index.html", navn=navn, forfatter=forfatter, sjanger=sjanger, hylle=hylle, elevNavn=elevNavn, elevProg=programfag)
        else:
            return "nope"
    else:
        form = request.form

        print(form)

        if form["submit"] == "Lei Ut":
            elevID = form["elevID"]
            dager = form["dager"]

            response = requests.post(url, json={"elevID": elevID, "dager": dager})
            return redirect(url_for("index", bokID=bokID))
        else:
            response = requests.post(url, json={"return": True})

if __name__ == "__main__":
    app.run(debug=True, port=8080)