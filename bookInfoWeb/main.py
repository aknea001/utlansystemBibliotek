from flask import Flask, render_template, session, request, redirect, url_for
from dotenv import load_dotenv
from os import getenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("FLASKPASSWD")

def generateCover(navn, forfatter):
    from PIL import Image, ImageDraw, ImageFont

    image = Image.open("bookInfoWeb/static/baseCover.jpg")
    draw = ImageDraw.Draw(image)

    fontNavn = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 50)
    fontForf = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 36)
    textColor = (0, 0, 0)

    navnTextLength = draw.textlength(navn, fontNavn)
    xNavn = (image.width - navnTextLength) / 2
    yNavn = image.height / 5

    forfTextLength = draw.textlength(forfatter, fontForf)
    xForf = (image.width - forfTextLength) / 2
    yForf = image.height / 3

    draw.text((xNavn, yNavn), navn, font=fontNavn, fill=textColor)
    draw.text((xForf, yForf), forfatter, font=fontForf, fill=textColor)
    image.save("bookInfoWeb/static/cover.jpg")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    

@app.route("/<bokID>", methods=["GET", "POST"])
def bokInfo(bokID):
    url = f"http://localhost:8000/bok/{bokID}"

    if request.method == "GET":
        response = requests.get(url)

        if response.status_code != 200:
            return f"error connecting to server: {response.status_code}"
        
        responseJson = response.json()
        bokInfo = responseJson["bokInfo"]
        elevInfo = responseJson["elevInfo"]

        navn = bokInfo["navn"]
        forfatter = bokInfo["forfatter"]
        sjanger = bokInfo["sjanger"]
        hylle = bokInfo["hylle"]

        generateCover(navn, str(forfatter))

        elevNavn = f"{elevInfo['navn']['first']} {elevInfo['navn']['last']}"
        programfag = elevInfo["programfag"]

        if responseJson["leid"]:
            session["leid"] = True
        else:
            session.clear()

        return render_template("bokInfo.html", navn=navn, forfatter=forfatter, sjanger=sjanger, hylle=hylle, elevNavn=elevNavn, elevProg=programfag)
    else:
        form = request.form

        #print(form)

        if form["submit"] == "Lei Ut":
            elevNavn = form["elevNavn"]
            dager = form["dager"]

            response = requests.get("http://localhost:8000/elev", headers={"elevNavn": elevNavn})

            if response.status_code == 200:
                elevID = response.json()["id"]
            else:
                return f"error: {response.status_code}"

            response = requests.post(url, json={"elevID": elevID, "dager": dager})
            return redirect(url_for("bokInfo", bokID=bokID))
        else:
            #print("returnerer")

            response = requests.post(url, json={"return": True})
            return redirect(url_for("bokInfo", bokID=bokID))

if __name__ == "__main__":
    app.run(debug=True, port=8080)