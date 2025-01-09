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

def elever(fornavn, etternavn, programfag):
    try:
        db = mysql.connector.connect(**sqlConfig)
        cursor = db.cursor()

        query = "INSERT INTO elever (fornavn, etternavn, programfag) \
                VALUES\
                (%s, %s, %s)"
        
        cursor.execute(query, (fornavn, etternavn, programfag))
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

        print(f"First: {first} \nLast: {last} \nProgramfag: {programfag}")

        elever(first, last, programfag)

if __name__ == "__main__":
    pass