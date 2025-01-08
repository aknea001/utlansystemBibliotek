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

        query = "SELECT\
                    e.*, \
                    GROUP_CONCAT(b.id SEPARATOR ',') AS bokIDer, \
                    GROUP_CONCAT(b.navn SEPARATOR ',') AS bokNavn, \
                    GROUP_CONCAT(IFNULL(b.forfatter, 'Ukjent Forfatter') SEPARATOR ',') AS bokForfattere, \
                    GROUP_CONCAT(IFNULL(b.sjanger, 'Ukjent Sjanger') SEPARATOR ',') AS bokSjangere \
                FROM elever e \
                LEFT JOIN utlan u ON e.id = u.elevID \
                LEFT JOIN boker b ON u.bokID = b.id \
                WHERE e.id = %s \
                GROUP BY e.id;"

        cursor.execute(query, (elevID, ))
        data = cursor.fetchone()

        if data:
            dataDic = {
                "userInfo": {
                    "id": data[0], 
                    "name": {
                        "first": data[1], 
                        "last": data[2]
                    }, 
                    "programfag": data[3], 
                    "registrert": data[4]
                },
                "utlanInfo": {
                    "bokIDer": data[5].split(","),
                    "bokNavn": data[6].split(","),
                    "bokForfattere": data[7].split(","),
                    "bokSjangere": data[8].split(",")
                }
            }
        else:
            return jsonify({"error": "No data found"}), 404
    except mysql.connector.Error as e:
        db = None
        return f"oopsie: {e}"
    finally:
        if db != None and db.is_connected():
            cursor.close()
            db.close()

    return jsonify(dataDic)

if __name__ == "__main__":
    app.run(debug=True, port=8000)