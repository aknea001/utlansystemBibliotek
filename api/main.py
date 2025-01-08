from flask import Flask, jsonify
import mysql.connector
from dotenv import load_dotenv
from os import getenv

load_dotenv()

sqlConfig = {
    "host": getenv("SQLHOST"),
    "user": getenv("SQLUSER"),
    "password": getenv("SQLPASSWD"),
    "database": getenv("SQLDATABASE")
}

app = Flask(__name__)

@app.route("/elev/<elevID>")
def elev(elevID):
    try:
        db = mysql.connector.connect(**sqlConfig)
        cursor = db.cursor()

        query = "SELECT * FROM elever WHERE id = %s"

        cursor.execute(query, (elevID, ))

        data = cursor.fetchone()
        dataDic = {
            "id": data[0], 
            "first": data[1], 
            "last": data[2], 
            "programfag": data[3], 
            "registrert": data[4]
        }

        return jsonify(dataDic)
    except mysql.connector.Error as e:
        db = None
        print(f"oopsie: {e}")
    finally:
        if db != None and db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    app.run(debug=True, port=8000)