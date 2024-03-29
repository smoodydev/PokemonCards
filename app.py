import os
from flask import Flask, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
import gspread
from google.oauth2.service_account import Credentials
import json
from read import createSet

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]



if os.path.exists("env.py"):
    import env
    DEVELOPMENT = True
else:
    DEVELOPMENT = False
    
p1 =os.environ.get("P1")
p2 =os.environ.get("P2")
p3 =os.environ.get("P3")
p4 =os.environ.get("P4")
p5 =os.environ.get("P5")

creds = {
  "type": "service_account",
  "project_id": "pokemonspreadsheet",
  "private_key_id": os.environ.get("GPKID"),
  "private_key": f"-----BEGIN PRIVATE KEY-----\n{p1}\n{p2}\n{p3}\n{p4}\n{p5}\nGcg5KJK9nQQSJS8pFuVFB8yaC5hJyuOMuDTgLt+r+hRM1Hih91Uo+bHRMHJlXFHY\nayia8VE3AgMBAAECggEASeqLdg7sf6glX2hTvdKO2QtC5ajO98CsXMFbsCoHsLzN\n4/7or39XV1RbcTMX6NvK03xYlbvef/oDMT44PAdklTrKG4mswuSxzTEN+0VK654H\nsLaUEH0C9PNC7iIQjKsjVIymF+c+/eYZWf5Tjbia/3oZqyLTaOFU+/5nBtWmkeA6\nT9o/zNT1F1N0bGP8803AJzBdcOdMTtwV40PIWefAOPAp6TnybMNiAzGifQ7YdFvM\n8b518oIzVYFcqG2smnFeNhoFtTDqWOXFs7MG1FvblCTawkyxNAOFT/Zrr3zabSDl\ngQ+9NyDQfPrp2Q5DaNlxTr2m3iUuNXGNS7xv5GONwQKBgQDPITNzgMmp/kuGq50/\nxPC9P71vtoa7Wh0OhDXTyFHGX4mUR2kPH4xPur3OGhbD4IfXNW8U2278J1MDkZ5t\napm0MjevAo3x6qY6CI0Xn3kfgyi1RFw6dZhCPcHICP/QWJwjfxTgzpNaURbWy1iL\nIdWHDX9LQ+6wa7BJSZarWIXO1QKBgQDMwrYI/NexGwuVavKWnn8JhpY6Iqa/zDV+\nB2jzDOqFGnwaPMnUHRWmAKBH0eS68h7jUD++ggrtv4jKk+neYcboCEuCvy/2BPK4\nUH9cIt9J53Ov41zIJhxJoCPyKgLMjCeDT4Au0R3w0Tor5AfmkwAqoUP/6I4Qd+NX\nhJbAWf5d2wKBgGZT17BTSs2xtKxGcjxD1k8Yg0UCXpOGVF6MkG8dQtEG99gKY2u2\nQUJOVmDQ4LhKX7HBUyxxr+Xgo5FaynLxvBeay4mpcGi4bQC0oset4E/iIyVSLWIw\nIFVxXx+s2nyamiCrMqxRQdjXwLnC4e5ye6Pp1h5f5DbCLOg387iY1ho1AoGBALKU\n5zqzelLGqbWpTuY6WcWvEfqmGhSRP94pDElebHOmA7LGbaiHrUfYp/G7h+fcH0BV\nzyKSPIHaWK2Fj6UaVeYsxd7EbEn/Ssmhu1JaP7AvIuC2RUdypZ05A+DC7yoC2rtV\nbRBn5dsQP9Hj0VgxwSVs/OeGpdCLH0ZHJ0ufsY+dAoGAHj8eSF9qvS9RzBDMHcqG\nLnYk2qxcCnowksbGYoMWmfPm8GwGPn9bFaEFdQM7QSxKqEIwg5Ln+jlipZ06l38e\nISToTC90DwhtOf7hNNQqufjka39xfAVYoCxseV1MTFfNyAsyKIOPgG9OLg0RJoYn\nAI98hrLde4Xl3oOPyGUY+pA=\n-----END PRIVATE KEY-----\n",
  "client_email": os.environ.get("GSEMAIL"),
  "client_id": os.environ.get("GSID"),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": os.environ.get("CERT_URI")
}

GSPREAD_CLIENT = gspread.service_account_from_dict(creds)
SHEET = GSPREAD_CLIENT.open('Pokemon Card Spreadsheet')

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "pokemomCards"

app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "")

app.secret_key = os.environ.get("SECRET_KEY", "")

app.templates = ""

mongo = PyMongo(app)

def b_test():
    print("SOMETHING")

@app.route('/')
def index():

    allSets = mongo.db.sets.find()
    return render_template("index.html", sets=allSets)

@app.route('/set/<set>')
def seeSet(set):
    theSet = mongo.db.sets.find_one({"setId": set})
    try:
        sheet = SHEET.worksheet(theSet["name"]).get_all_values()
        have = 0
        if len(sheet[0]) > 1:
            for c in sheet:
                if c[1]:
                    have += 1
        mongo.db.sets.update_one({"setId": set}, {"$set": {"set_total": len(sheet), "have": have}})
        return render_template("sets.html", set=theSet, cards=sheet)
    except:
        if "user" in session:
            theSet = mongo.db.sets.find_one({"setId": set})
            createSet(theSet, SHEET)
            return render_template("sets.html", set=theSet, cards=sheet)
    return redirect(url_for("index"))

@app.route('/update/<set>/<num>')
def updateCardInSet(set, num):
    theSet = mongo.db.sets.find_one({"setId": set})["name"]
    # print(theSet["name"])
    if "user" in session:
        sheet = SHEET.worksheet(theSet)
        have = (sheet.get("B"+str(num)))
        if have:
            sheet.update("B"+str(num), "")
        else:
            sheet.update("B"+str(num), 1)
    return redirect(url_for('seeSet', set=set))

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        passwordIN = request.form.get("password")
        if passwordIN == os.environ.get("PASSWORD", ""):
            session["user"] = "admin"
            print(session["user"])
    return redirect("/")


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT', 8080)),
            debug=DEVELOPMENT)