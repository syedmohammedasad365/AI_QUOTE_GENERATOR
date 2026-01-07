'''import requests
import os
from dotenv import load_dotenv
api_key=os.getenv("hf_api_key")
if not api_key:
    print("Api key not found")
hearders='{"authorization":f"bearer {api_key}}'
url="https://huggingface.co/"
payload={"inputs":"write a quotation for success"}
data= requests.post(url,headers=hearders,json=payload)
result=data.json()
print(result)'''

from flask import Flask, jsonify, render_template, request, redirect, session
import requests
import os
import mysql.connector
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# API Configuration
API_KEY = "mfgDat4DNF6f+QbbipA1Kg==EWt5d3lxWvioJs7O"
API_URL = "https://api.api-ninjas.com/v2/randomquotes"
HEADERS = {"X-Api-Key": API_KEY}

# Database Connection Function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )

@app.route("/", methods=["GET"])
def quotation():
    return render_template("index.html")

@app.route("/quote", methods=["GET"])
def get_online_quote():
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "quote": data[0]["quote"],
            "author": data[0]["author"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/home")
def home():
    if "user" in session:
        return render_template("home.html", username=session["user"])
    return redirect("/login")

@app.route("/regi", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        
        try:
            db = get_db_connection()
            cursor = db.cursor()
            query = "INSERT INTO registration (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, password))
            db.commit()
            cursor.close()
            db.close()
            return "Registration successful! <a href='/login'>Login now</a>"
        except mysql.connector.Error as err:
            return f"Database Error: {err}"

    return render_template("regi.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            query = "SELECT * FROM registration WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            cursor.close()
            db.close()

            if user:
                session["user"] = user["username"]
                return redirect("/home")
            else:
                return "Invalid credentials! <a href='/login'>Try again</a>"
        except mysql.connector.Error as err:
            return f"Database Error: {err}"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)

#jinja - whatever framework/templaate in python if needed to convert into html then we use jinja