from flask import Flask, render_template, session, request, redirect, url_for
from dotenv import load_dotenv
from os import getenv
import requests
from random import choice, randint
from string import ascii_uppercase
from qrMaker import makeQR

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("BOKINFOKEY")

apiUrl = "http://localhost:8000"

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

def generateHylle():
    hylleTall = randint(1, 99)

    if hylleTall < 10:
        hylleTall = "0" + str(hylleTall)

    hylleBokstav = choice(ascii_uppercase)

    hylle = str(hylleTall) + hylleBokstav

    return hylle

def getJWT():
    res = requests.get(apiUrl + "/getJWT", headers={"biblio": "biblio1", "biblioToken": getenv("biblioToken")})

    if res.status_code != 200:
        return f"Error getting access token: {res.status_code}"
    
    session["accessToken"] = res.json()["accessToken"]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    if "skipSearch" in request.form:
        tittel = request.form["tittel"]
        session["tittel"] = tittel
        return render_template("index.html", tittel=tittel)
    
    if "forfatter" not in request.form:
        tittel = str(request.form["tittel"]).strip().replace(" ", "+")

        if len(tittel) == 10 or 13:
            try:
                int(tittel)

                url = f"https://openlibrary.org/isbn/{tittel}.json"

                response = requests.get(url)

                if response.status_code == 200:
                    tittel = str(response.json()["title"]).strip().replace(" ", "+")
                else:
                    return f"error: {response.status_code}"
            except ValueError:
                pass

        url = f"https://openlibrary.org/search.json?q={tittel}"
        response = requests.get(url)

        if response.status_code != 200:
            return f"error: {response.status_code}"
        
        if response.json()["docs"]:
            docs = response.json()["docs"][0]

            forfatter = docs["author_name"][0]
            if "subject" in docs:
                sjanger = choice(docs["subject"])
            else:
                sjanger = ""
        else:
            forfatter = ""
            sjanger = ""

        tittel = tittel.replace("+", " ")
        session["tittel"] = tittel

        return render_template("index.html", tittel=tittel, forfatter=forfatter, sjanger=sjanger)

    form = request.form
    tittel = str(form["tittel"])
    forfatter = str(form["forfatter"])
    sjanger = str(form["sjanger"])

    hylle = generateHylle()

    for i in range(2):
        try:
            response = requests.post(apiUrl + "/bok", headers={"Authorization": f"Bearer {session['accessToken']}"}, json={"tittel": tittel, "forfatter": forfatter, "sjanger": sjanger, "hylle": hylle})
            break
        except KeyError:
            getJWT()

    if response.status_code != 200:
        return response.json()
    
    session.clear()

    if "success" in response.json():
        makeQR(response.json()["id"])
        return render_template("index.html", qrcode=True, gammelTittel=tittel)
    
    return response.json()
    
@app.route("/clear")
def clear():
    session.clear()
    return redirect(url_for("index"))

@app.route("/reservert")
def reservert():
    getJWT()

    response = requests.get(apiUrl + "/bok/reservert", headers={"Authorization": f"Bearer {session['accessToken']}"})

    if response.status_code != 200:
        return str(response.status_code)
    
    data = response.json()

    return render_template("reservert.html", reservert=data)

@app.route("/<bokID>", methods=["GET", "POST"])
def bokInfo(bokID):
    url = f"{apiUrl}/bok/{bokID}"

    for i in range(2):
        try:
            headers = {"Authorization": f"Bearer {session['accessToken']}"}
            break
        except KeyError:
            getJWT()

    if request.method == "GET":
        response = requests.get(url, headers=headers)

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

        return render_template("bokInfo.html", navn=navn, forfatter=forfatter, sjanger=sjanger, hylle=hylle, elevNavn=elevNavn, elevProg=programfag, reservertNavn=elevNavn if responseJson["reservertKlar"] else None, reservertIkkeKlar=responseJson["reservert"] and not responseJson["reservertKlar"])
    else:
        form = request.form

        print(form)

        if form.get("reservert", None) == "true":
            res = requests.post(apiUrl + "/bok/reservert/update", json={"klar": False, "bokID": bokID}, headers=headers)

        if form["submit"] == "Lei Ut":
            elevNavn = form["elevNavn"]
            dager = form["dager"]

            response = requests.get(apiUrl + "/elev/info", headers={"elevNavn": elevNavn})

            if response.status_code == 200:
                elevID = response.json()["id"]
            else:
                return f"error: {response.status_code}"

            response = requests.post(url, json={"elevID": elevID, "dager": dager}, headers=headers)
            return redirect(url_for("bokInfo", bokID=bokID))
        else:
            #print("returnerer")

            response = requests.post(url, json={"return": True}, headers=headers)
            return redirect(url_for("bokInfo", bokID=bokID))

if __name__ == "__main__":
    app.run(debug=True, port=8080)