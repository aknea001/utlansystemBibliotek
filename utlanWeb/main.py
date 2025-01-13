from flask import Flask, session, render_template, url_for, request
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

@app.route("/profile")
def elevInfo():
    url = f"http://localhost:8000/elev"

    response = requests.get(url, headers={"elevID": "6"})

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

    return render_template("elevPage.html", navn=navn["first"], leid=data["leid"], utlan=utlanLst)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    user = request.form["user"]
    passwd = request.form["passwd"]

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    user = request.form["user"]
    passwd = request.form["passwd"]
    passwdCheck = request.form["passwdCheck"]

if __name__ == "__main__":
    app.run(debug=True)