from flask import Flask, session, render_template, url_for, request, redirect
from dotenv import load_dotenv
from os import getenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("FLASKPASSWD")
app.jinja_env.filters["zip"] = zip

@app.route("/")
def index():
    return render_template("index.html")

def hash(passwd, salt):
    import hashlib

    flavorPass = str(passwd) + str(salt)

    hashObj = hashlib.sha256(flavorPass.encode())
    hashed = hashObj.hexdigest()

    return hashed

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    user = request.form["user"]
    passwd = request.form["passwd"]

    url = "http://localhost:8000/elev"
    response = requests.get(url, headers={"username": str(user), "salt": "True"})

    if response.status_code == 200:
        salt = response.json()["salt"]
    else:
        return f"error: {response.status_code}"
    
    hashed = hash(passwd, salt)

    response = requests.get(url, headers={"username": str(user), "hash": hashed})

    if response.status_code == 200:
        elevID = response.json()["elevID"]
    elif response.status_code == 404:
        return "Wrong credentials"
    else:
        return f"error: {response.status_code}"
    
    session["elevID"] = elevID

    if "redirectUrl" in session:
        return redirect(session["redirectUrl"])

    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def generateCover(navn, forfattere, amount):
    from PIL import Image, ImageDraw, ImageFont

    for i in range(amount):
        image = Image.open("bookInfoWeb/static/baseCover.jpg")
        draw = ImageDraw.Draw(image)

        fontNavn = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 50)
        fontForf = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 36)
        textColor = (0, 0, 0)

        navnTextLength = draw.textlength(navn[i], fontNavn)
        xNavn = (image.width - navnTextLength) / 2
        yNavn = image.height / 5

        forfTextLength = draw.textlength(forfattere[i], fontForf)
        xForf = (image.width - forfTextLength) / 2
        yForf = image.height / 3

        draw.text((xNavn, yNavn), navn[i], font=fontNavn, fill=textColor)
        draw.text((xForf, yForf), forfattere[i], font=fontForf, fill=textColor)
        image.save(f"utlanWeb/static/cover{i}.jpg")

@app.route("/profile")
def elevInfo():
    if "elevID" not in session:
        session["redirectUrl"] = url_for("elevInfo")
        return redirect(url_for("login"))

    url = "http://localhost:8000/elev"

    response = requests.get(url, headers={"elevID": str(session["elevID"])})

    if response.status_code != 200:
        return f"error connecting to server: {response.status_code}"
    
    data = response.json()
    userInfo = data["userInfo"]

    navn = userInfo["name"]

    utlanLst = []
    
    if data["leid"]:
        utlanInfo = data["utlanInfo"]
        bokNavn = utlanInfo["bokNavn"]
        bokForfattere = utlanInfo["bokForfattere"]

        tempUtlanLst = []

        for i in range(len(bokNavn)):
            tempUtlanLst.append(bokNavn[i])
            tempUtlanLst.append(bokForfattere[i])

            utlanLst.append(tempUtlanLst)
            tempUtlanLst = []

        generateCover(bokNavn, bokForfattere, len(bokNavn))

    return render_template("elevPage.html", navn=navn["first"], leid=data["leid"], utlan=utlanLst)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    user = request.form["user"]
    passwd = request.form["passwd"]
    passwdCheck = request.form["passwdCheck"]

if __name__ == "__main__":
    app.run(debug=True)