from flask import Flask, render_template, session
from dotenv import load_dotenv
from os import getenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("FLASKPASSWD")

@app.route("/<bokID>")
def index(bokID):
    url = f"http://localhost:8000/bok/{bokID}"
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

if __name__ == "__main__":
    app.run(debug=True, port=8080)