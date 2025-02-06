from flask import Flask, session, render_template, url_for, request, redirect
from dotenv import load_dotenv
from os import getenv
from secrets import token_hex
import requests
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("UTLANKEY")
app.permanent_session_lifetime = timedelta(days=1)

apiUrl = "http://localhost:8000"

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
        image.save(f"utlanWeb/static/covers/cover{i}.jpg")

@app.route("/")
def index():
    if "page" not in request.args or int(request.args["page"]) < 1:
        return redirect("/?page=1")

    session.pop("registrert", None)

    page = request.args["page"]

    convertedPage = (int(page) - 1) * 8

    search = None

    if "search" in request.args:
        search = request.args["search"]
        response = requests.get(apiUrl + "/bok", headers={"page": str(convertedPage), "searchQuery": search})
    else:
        response = requests.get(apiUrl + "/bok", headers={"page": str(convertedPage)})
    
    if response.status_code != 200:
        return f"oopsie: {response.status_code}"
    
    data = response.json()

    if len(data) == 9:
        del data[-1:]
        nextPage = True
    else:
        nextPage = False

    bokNavn = []
    bokForfattere = []

    #Change to json in API so this shit is less scuffed

    for i in data:
        bokNavn.append(i[1])
        bokForfattere.append(str(i[2]))

    generateCover(bokNavn, bokForfattere, len(bokNavn))

    return render_template("index.html", boker=data, page=int(page), nextPage=nextPage, search=search)

def hash(passwd, salt):
    import hashlib

    flavorPass = str(passwd) + str(salt)

    hashObj = hashlib.sha256(flavorPass.encode())
    hashed = hashObj.hexdigest()

    return hashed

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session.clear()
        return render_template("login.html")
    
    user = request.form["navn"]

    if "passwd" not in request.form:
        response = requests.get(apiUrl + "/elev/info", headers={"elevNavn": str(user)})

        if response.status_code != 200:
            return f"error connecting to API: {response.status_code}"
        
        if response.json()["registrert"] == "f":
            return render_template("register.html", elevNavn=user)
        else:
            session["registrert"] = True
            return render_template("login.html", elevNavn=user)
    
    passwd = request.form["passwd"]

    response = requests.get(apiUrl + "/getJWT", headers={"elevNavn": str(user), "passwd": str(passwd)})

    if response.status_code == 200:
        session.permanent = True
        session["accessToken"] = response.json()["accessToken"]
    elif response.status_code == 404:
        return "Wrong credentials"
    else:
        return f"error: {response.status_code}"

    if "redirectUrl" in session:
        return redirect(session["redirectUrl"])

    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/profile")
def elevInfo():
    if "accessToken" not in session:
        session["redirectUrl"] = url_for("elevInfo")
        return redirect(url_for("login"))


    response = requests.get(apiUrl + "/elev", headers={"Authorization": f"Bearer {session["accessToken"]}"})

    if response.status_code == 401:
        session.clear()
        return redirect(url_for("elevInfo"))
    elif response.status_code != 200:
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
    
    user = request.form["elevNavn"]
    passwd = request.form["passwd"]
    passwdCheck = request.form["passwdCheck"]

    if passwd != passwdCheck:
        return "passwords not matching"
    
    salt = token_hex(32)
    hashed = hash(passwd, salt)
    

    response = requests.get(apiUrl + "/elev/info", headers={"elevNavn": user})

    if response.status_code != 200:
        return f"error connecting to database: {response.status_code}"
    
    elevID = response.json()["id"]

    response = requests.post(apiUrl + "/elev/update", json={"hash": hashed, "salt": salt, "elevID": elevID})

    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)