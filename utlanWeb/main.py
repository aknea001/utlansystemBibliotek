from flask import Flask, session, render_template, url_for, request
from dotenv import load_dotenv
from os import getenv
import requests

load_dotenv()

app = Flask(__name__)
#app.secret_key = getenv("FLASKPASSWD")
app.jinja_env.filters["zip"] = zip

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/<elevID>")
def elevInfo(elevID):
    url = f"http://localhost:8000/elev/{elevID}"

    response = requests.get(url)

    if response.status_code != 200:
        return f"error connecting to server: {response.status_code}"
    
    data = response.json()
    userInfo = data["userInfo"]

    navn = userInfo["name"]

    return render_template("elevPage.html", navn=navn["first"])
        

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