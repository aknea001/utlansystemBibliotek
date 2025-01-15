from flask import Flask, jsonify, request
from flask_cors import CORS
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
CORS(app)

@app.route("/elev")
def elev():
    if "elevID" in request.headers:
        elevID = int(request.headers["elevID"])

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
        except mysql.connector.Error as e:
            db = None
            return jsonify({"error": f"mysql error: {e}"})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()

        if data:
            dataDic = {
                    "userInfo": {
                        "id": data[0], 
                        "name": {
                            "first": data[1], 
                            "last": data[2]
                        }, 
                        "programfag": data[3], 
                        "registrert": data[4],
                        "hash": data[5],
                        "salt": data[6]
                    },
                    "leid": False
                }
            
            if data[7]:
                dataDic["leid"] = True
                dataDic["utlanInfo"] = {
                                "bokIDer": data[7].split(","),
                                "bokNavn": data[8].split(","),
                                "bokForfattere": data[9].split(","),
                                "bokSjangere": data[10].split(",")
                            }

            return jsonify(dataDic)
        else:
            return jsonify({"error": "No data found"}), 404
    elif ("username" and "hash") in request.headers:
        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            query = "SELECT id FROM elever WHERE fornavn = %s AND hash = %s"

            cursor.execute(query, (request.headers["username"], request.headers["hash"]))
            data = cursor.fetchone()
        except mysql.connector.Error as e:
            db = None
            return jsonify({"error": f"mysql error: {e}"})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()

        if data:
            dataDic = {
                    "elevID": data[0]
            }

            return jsonify(dataDic)
        else:
            return jsonify({"error": "No data found"}), 404
    elif ("username" and "salt") in request.headers:
        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            query = "SELECT salt FROM elever WHERE fornavn = %s"

            cursor.execute(query, (request.headers["username"], ))
            data = cursor.fetchone()
        except mysql.connector.Error as e:
            db = None
            return jsonify({"error": f"mysql error: {e}"})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()

        if data:
            dataDic = {
                    "salt": data[0]
            }

            return jsonify(dataDic)
        else:
            return jsonify({"error": "No data found"}), 404
    elif "elevNavn" in request.headers:
        fullNavn = request.headers["elevNavn"]
        fullNavnLst = fullNavn.split(" ")

        first = fullNavnLst[0]
        last = fullNavnLst[1]
        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            query = "SELECT id FROM elever WHERE fornavn = %s AND etternavn = %s"
            cursor.execute(query, (first, last))

            data = cursor.fetchone()
        except mysql.connector.Error as e:
            db = None
            return jsonify({"error": f"mysql error: {e}"})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()

        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "no data found"})
    else:
        return jsonify({"error": "Missing headers"})
    
@app.route("/elevNavn")
def elevNavn():
    if "searchQuery" not in request.headers:
        return jsonify({"error": "missing headers"}), 404

    try:
        db = mysql.connector.connect(**sqlConfig)
        cursor = db.cursor()

        query = "SELECT fornavn, etternavn FROM elever WHERE fornavn LIKE %s LIMIT 4"

        cursor.execute(query, (f"{request.headers['searchQuery']}%", ))
        data = cursor.fetchall()
    except mysql.connector.Error as e:
        db = None
        return jsonify({"error": f"database error {e}"})
    finally:
        if db != None and db.is_connected():
            cursor.close()
            db.close()
        
    if data:
        return jsonify(data)
    else:
        return jsonify([])

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
    app.run(debug=True, port=8000)