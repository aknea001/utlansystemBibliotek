from flask import Flask, jsonify, request
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

@app.route("/bok/<bokID>", methods=["GET", "POST"])
def bok(bokID):
    if request.method == "GET":
        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            query = "SELECT \
                        b.*, \
                        e.id AS elevID, \
                        e.fornavn, \
                        e.etternavn, \
                        e.programfag \
                    FROM boker b \
                    LEFT JOIN utlan u ON b.id = u.bokID \
                    LEFT JOIN elever e ON u.elevID = e.id \
                    WHERE b.id = %s;"

            cursor.execute(query, (bokID, ))
            data = cursor.fetchone()

            if data:
                dataDic = {
                    "bokInfo": {
                        "id": data[0],
                        "navn": data[1],
                        "forfatter": data[2],
                        "sjanger": data[3],
                        "hylle": data[4]
                    },
                    "leid": data[5] != None,
                    "elevInfo": {
                        "elevID": data[5],
                        "navn": {
                            "first": data[6],
                            "last": data[7]
                        },
                        "programfag": data[8]
                    }
                }
            else:
                return jsonify({"error": "No data found"}), 404
        except mysql.connector.Error as e:
            db = None
            return(f"oopsie: {e}")
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()

        return jsonify(dataDic)
    else:
        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()
        except mysql.connector.Error as e:
            return jsonify({"success": False, "error": str(e)})

        try:
            query = "INSERT INTO utlan (bokID, elevID, sluttDato) \
                    VALUES \
                    (%s, %s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL %s DAY))"
            
            postData = request.json

            #print(postData)
            
            cursor.execute(query, (bokID, postData["elevID"], postData["dager"]))
            db.commit()

            return jsonify({"success": True})
        except KeyError as e:
            try:
                if postData["return"]:
                    #print("returning..")

                    query = "DELETE FROM utlan WHERE bokID = %s"

                    cursor.execute(query, (bokID, ))
                    db.commit()

                    return jsonify({"success": True})
            except KeyError:
                db = None
                return jsonify({"success": False, "error": f"Wrong Key: {e}"})
        except mysql.connector.Error as e:
            db = None
            return jsonify({"success": False, "error": str(e)})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()

if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")