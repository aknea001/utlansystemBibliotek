import mysql.connector
from dotenv import load_dotenv
from os import getenv
import requests
from random import randint, choice

load_dotenv()

sqlConfig = {
    "host": getenv("SQLHOST"),
    "user": getenv("SQLUSER"),
    "password": getenv("SQLPASSWD"),
    "database": getenv("SQLDATABASE")
}

def elever(fornavn, etternavn, programfag, hashed, salt):
    try:
        db = mysql.connector.connect(**sqlConfig)
        cursor = db.cursor()

        query = "INSERT INTO elever (fornavn, etternavn, programfag, hash, salt) \
                VALUES\
                (%s, %s, %s, %s, %s)"
        
        cursor.execute(query, (fornavn, etternavn, programfag, hashed, salt))
        db.commit()
    except mysql.connector.Error as e:
        db = None
        print(f"Oopsie: {e}")
    finally:
        if db != None and db.is_connected():
            cursor.close()
            db.close()

def addElever(count):
    for i in range(count):
        url = "https://randomuser.me/api/?nat=no,dk,nl,us"

        response = requests.get(url)

        if response.status_code == 200:
            fullName = response.json()["results"][0]["name"]
            first = fullName["first"]
            last = fullName["last"]

        linjer1 = ["ST", "MK", "IM"]
        linjer2 = ["ST", "MK", "MP", "IT"]
        trinn = randint(1, 2)

        if trinn == 1:
            linje = choice(linjer1)
        else:
            linje = choice(linjer2)

        programfag = str(trinn) + str(linje)

        hashed, salt = addPassword()

        print(f"First: {first} \nLast: {last} \nProgramfag: {programfag}")

        elever(first, last, programfag, hashed, salt)

def passordHash(hash, salt, id):
    try:
        db = mysql.connector.connect(**sqlConfig)
        cursor = db.cursor()

        query = "UPDATE elever \
                SET hash = %s, salt = %s \
                WHERE id = %s"

        cursor.execute(query, (hash, salt, id))
        db.commit()

        print("Success..")
    except mysql.connector.Error as e:
        db = None
        print(f"oopsie: {e}")
    finally:
        if db != None and db.is_connected():
            cursor.close()
            db.close()

def addPassword(count=None):
    import hashlib
    from secrets import token_hex

    passwd = "password"
    salt = token_hex(32)

    flavorPass = passwd + str(salt)

    hashObj = hashlib.sha256(flavorPass.encode())
    hashed = hashObj.hexdigest()

    return hashed, salt

    #passordHash(hashed, salt, i + 1)

def boker(navn, forfatter, sjanger, hylle):
    try:
        db = mysql.connector.connect(**sqlConfig)
        cursor = db.cursor()

        query = "INSERT INTO boker (navn, forfatter, sjanger, hylle) \
                VALUES \
                (%s, %s, %s, %s)"
        
        cursor.execute(query, (navn, forfatter, sjanger, hylle))
        db.commit()

        print(f"Successfully added {navn} by {forfatter}")
    except mysql.connector.Error as e:
        db = None
        print(f"woopise: {e}")
    finally:
        if db != None and db.is_connected():
            cursor.close()
            db.close()

def apiGet(url):
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code

def addBoker(count):
    import string

    for i in range(count):
        adjective = apiGet("https://random-word-form.herokuapp.com/random/adjective")[0]
        noun = apiGet("https://random-word-form.herokuapp.com/random/noun")[0]
        
        title = f"The {adjective} {noun}"

        fullName = apiGet("https://randomuser.me/api/?nat=no,dk,nl,us")["results"][0]["name"]

        forfatter = f"{fullName['first']} {fullName['last']}"

        henry = randint(1,20)
        if henry == 8:
            forfatter = "Henry Dang"

        sjanger = apiGet("https://random-word-form.herokuapp.com/random/adjective")[0]

        hylleTall = randint(1, 99)

        if hylleTall < 10:
            hylleTall = "0" + str(hylleTall)

        hylleBokstav = choice(string.ascii_uppercase)

        hylle = str(hylleTall) + hylleBokstav

        print(f"Navn: {title} \nForfatter: {forfatter} \nSjanger: {sjanger} \nHylle: {hylle}")
        boker(title, forfatter, sjanger, hylle)

if __name__ == "__main__":
    pass