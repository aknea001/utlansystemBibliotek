from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
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
app.config["JWT_SECRET_KEY"] = getenv("JWTKEY")
CORS(app)
jwt = JWTManager(app)

def hash(passwd, salt):
    import hashlib

    flavorPass = str(passwd) + str(salt)

    hashObj = hashlib.sha256(flavorPass.encode())
    hashed = hashObj.hexdigest()

    return hashed

@app.route("/getJWT")
def getJWT():
    if ("elevNavn" and "passwd") in request.headers:
        fullNavn = request.headers["elevNavn"]
        fullNavnLst = fullNavn.split(" ")

        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            print(f"{fullNavn[0]} {fullNavn[1]}")

            query = "SELECT salt FROM elever WHERE fornavn = %s AND etternavn = %s"

            cursor.execute(query, (fullNavnLst[0], fullNavnLst[1]))
            salt = cursor.fetchone()[0]
        except mysql.connector.Error as e:
            db = None
            return jsonify({"error": f"mysql error: {e}"})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()

        hashed = hash(request.headers["passwd"], salt)

        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            query = "SELECT id FROM elever WHERE fornavn = %s AND etternavn = %s AND hash = %s"

            cursor.execute(query, (fullNavnLst[0], fullNavnLst[1], hashed))
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
                    "accessToken": create_access_token(str(data[0]))
            }

            return jsonify(dataDic)
        else:
            return jsonify({"error": "No data found"}), 404
    elif "elevNavn" in request.headers:
        fullNavn = request.headers["elevNavn"]
        fullNavnLst = fullNavn.split(" ", 1)

        first = fullNavnLst[0]
        last = fullNavnLst[1]
        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            query = "SELECT id, registrert FROM elever WHERE fornavn = %s AND etternavn = %s"
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
            dataDic = {
                "id": data[0],
                "registrert": data[1]
            }
            return jsonify(dataDic)
        else:
            return jsonify({"error": "no data found"}), 404
    elif ("biblio" and "biblioToken") in request.headers:
        if request.headers["biblioToken"] == getenv("biblioToken"):
            return jsonify({"accessToken": create_access_token(str(request.headers["biblio"]))})
        else:
            return jsonify({"error": "no data found"}), 404
    else:
        return jsonify({"error": "Missing headers"})

@app.route("/elev", methods=["GET", "POST"])
@jwt_required()
def elev():
    if request.method == "GET":
        try:
            elevID = get_jwt_identity()

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
    else:
        postData = request.json
        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            query = "UPDATE elever \
                    SET hash = %s, salt = %s, registrert = 't' \
                    WHERE id = %s"
            
            cursor.execute(query, (postData["hash"], postData["salt"], postData["elevID"]))
            db.commit()

            return jsonify({"success": True})
        except KeyError:
            return jsonify({"error": "Wrong key"})
        except mysql.connector.Error as e:
            db = None
            return jsonify({"error": f"database error: {e}"})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()
    
@app.route("/elevNavn")
def elevNavn():
    if "searchQuery" not in request.headers:
        return jsonify({"error": "missing headers"}), 404

    try:
        db = mysql.connector.connect(**sqlConfig)
        cursor = db.cursor()

        if "fornavn" not in request.headers:
            query = "SELECT fornavn, etternavn FROM elever WHERE fornavn LIKE %s LIMIT 4"
            cursor.execute(query, (f"{request.headers['searchQuery']}%", ))
        else:
            query = "SELECT fornavn, etternavn FROM elever WHERE fornavn = %s AND etternavn LIKE %s LIMIT 4"
            cursor.execute(query, (request.headers["fornavn"], f"{request.headers['searchQuery']}%"))

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
                        e.programfag, \
                        u.reservert, \
                        u.reservertKlar \
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
                    "leid": data[5] != None and data[9] == "f",
                    "reservert": data[9] == "t",
                    "reservertKlar": data[10] == "t",
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
            query = "INSERT INTO utlan (bokID, elevID, reservert, sluttDato) \
                    VALUES \
                    (%s, %s, %s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL %s DAY))"
            
            postData = request.json

            #print(postData)
            
            cursor.execute(query, (bokID, postData["elevID"], "f", postData["dager"]))
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

@app.route("/bok", methods=["GET"])
def boker():
    if request.method == "GET":
        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            if "searchQuery" not in request.headers:
                query = "SELECT \
                            b.*, \
                            u.bokID \
                        FROM boker b \
                        LEFT JOIN utlan u ON b.id = u.bokID \
                        LIMIT %s,9"

                cursor.execute(query, (int(request.headers["page"]), ))
                data = cursor.fetchall()

                #Change to json so this shit is less scuffed
                return jsonify(data)
            
            searchQuery = request.headers["searchQuery"]
            query = "SELECT \
                            b.*, \
                            u.bokID \
                        FROM boker b \
                        LEFT JOIN utlan u ON b.id = u.bokID \
                        WHERE navn LIKE %s \
                        OR navn LIKE %s \
                        OR forfatter LIKE %s \
                        OR forfatter LIKE %s \
                        LIMIT %s,9"

            cursor.execute(query, (f"{searchQuery}%", f"The {searchQuery}%", f"{searchQuery}%", f"% {searchQuery}%", int(request.headers["page"])))
            data = cursor.fetchall()

            #Change to json so this shit is less scuffed
            return jsonify(data)
        except mysql.connector.Error as e:
            db = None
            return jsonify({"error": f"database error: {e}"})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()

@app.route("/bok/add", methods=["POST"])
@jwt_required()
def addBoker():
    if "biblio" not in get_jwt_identity():
        return jsonify({"error": "Unauthorized"}), 403

    try:
        db = mysql.connector.connect(**sqlConfig)
        cursor = db.cursor()

        query = "INSERT INTO boker (navn, forfatter, sjanger, hylle) \
                VALUES \
                (%s, %s, %s, %s)"

        postData = request.json

        cursor.execute(query, (postData["tittel"], postData["forfatter"], postData["sjanger"], postData["hylle"]))
        db.commit()

        return jsonify({"success": True, "id": cursor.lastrowid})
    except KeyError:
        return jsonify({"error": "Wrong Key"})
    except mysql.connector.Error as e:
        db = None
        return jsonify({"error": f"Database error: {e}"})
    finally:
        if db != None and db.is_connected():
            cursor.close()
            db.close()

@app.route("/bok/reservert", methods=["GET", "POST"])
def reservert():
    if request.method == "GET":
        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()
            
            query = "SELECT \
                        u.*, \
                        b.navn, \
                        b.forfatter, \
                        b.hylle \
                    FROM utlan u \
                    LEFT JOIN boker b ON u.bokID = b.id \
                    WHERE u.reservert = 't' \
                    AND u.reservertKlar = 'f'"
            
            cursor.execute(query)
            data = cursor.fetchall()

            dataLst = []

            for i in data:
                dic = {
                    "elevID": i[2],
                    "bokID": i[1],
                    "tittel": i[7],
                    "forfatter": i[8],
                    "hylle": i[9]
                }

                dataLst.append(dic)

            return jsonify(dataLst)
        except mysql.connector.Error as e:
            db = None
            return jsonify({"error": f"Database Error: {e}"})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()
    elif request.method == "POST":
        data = request.json

        try:
            db = mysql.connector.connect(**sqlConfig)
            cursor = db.cursor()

            if "klar" not in data:
                query = "INSERT INTO utlan (bokID, elevID, reservert, reservertKlar, sluttDato) \
                        VALUES \
                        (%s, %s, %s, %s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL %s DAY))"
                
                cursor.execute(query, (data["bokID"], data["elevID"], "t", "f", 2))
                db.commit()
                
                return jsonify({"Success": True})
            
            if data["klar"]:
                query = "UPDATE utlan \
                        SET reservertKlar = %s \
                        WHERE bokID = %s and reservert = %s"
                
                cursor.execute(query, ("t", data["bokID"], "t"))
                db.commit()

                return jsonify({"success": True})
            elif not data["klar"]:
                query = "DELETE FROM utlan \
                        WHERE bokID = %s and reservert = %s"
                
                cursor.execute(query, (data["bokID"], "t"))
                db.commit()

                return jsonify({"success": True})
        except mysql.connector.Error as e:
            db = None
            return jsonify({"error": f"Database Error: {e}"})
        finally:
            if db != None and db.is_connected():
                cursor.close()
                db.close()

if __name__ == "__main__":
    app.run(debug=True, port=8000)