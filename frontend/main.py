from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
import sqlite3
import markdown

app = Flask(__name__)

# Project structure setup
FRONTEND_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(FRONTEND_DIR)

# Connect to overview.db in the same directory as this file (frontend/)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(FRONTEND_DIR, "overview.db")
app.config["SQLALCHEMY_ECHO"] = False
db = SQLAlchemy(app)

# Models
class Overview(db.Model):
    __tablename__ = "overview"
    id = db.Column(db.Integer, primary_key=True)
    field = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)

class employment(db.Model):
    __tablename__ = "employment"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)
    is_employment = db.Column(db.Boolean, nullable=True)

class Housing(db.Model):
    __tablename__ = "housing"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)

class Transit(db.Model):
    __tablename__ = "transit"
    id = db.Column(db.Integer, primary_key=True)
    is_transit = db.Column(db.Boolean, nullable=True)
    status = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)

class Healthcare(db.Model):
    __tablename__ = "healthcare"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)

class Placemaking(db.Model):
    __tablename__ = "placemaking"
    id = db.Column(db.Integer, primary_key=True)
    is_school = db.Column(db.Boolean, nullable=True)
    status = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)

# Fetch Helpers
def fetch_employment():
    try:
        employed = employment.query.filter_by(is_employment=True).all()
        unemployed = employment.query.filter_by(is_employment=False).all()
        return employed, unemployed
    except Exception as e:
        print(f"Error fetching employment data: {e}")
        return [], []

def fetch_housing():
    try:
        return Housing.query.all()
    except Exception as e:
        print(f"Error fetching housing data: {e}")
        return []

def fetch_transit():
    try:
        grt = Transit.query.filter_by(is_transit=True).all()
        go = Transit.query.filter_by(is_transit=False).all()
        return grt, go
    except Exception as e:
        print(f"Error fetching transit data: {e}")
        return [], []

def fetch_healthcare():
    try:
        return Healthcare.query.all()
    except Exception as e:
        print(f"Error fetching healthcare data: {e}")
        return []

def fetch_placemaking():
    try:
        schools = Placemaking.query.filter_by(is_school=True).all()
        ghg = Placemaking.query.filter_by(is_school=False).all()
        return schools, ghg
    except Exception as e:
        print(f"Error fetching placemaking data: {e}")
        return [], []

# Ensure tables exist
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    try:
        rows = Overview.query.all()
    except Exception as e:
        print(f"Error querying Overview table: {e}")
        rows = []
        
    emp_data, unemp_data = fetch_employment()
    housing_data = fetch_housing()
    transit_data, go_data = fetch_transit()
    healthcare_data = fetch_healthcare()
    school_data, ghg_data = fetch_placemaking()
    
    return render_template("index.html", 
                           rows=rows, 
                           unemployment=unemp_data, 
                           employment=emp_data,
                           housing=housing_data,
                           transit=transit_data,
                           go_train=go_data,
                           healthcare=healthcare_data,
                           schools=school_data,
                           ghg=ghg_data)

@app.route("/goals")
def goals():
    db_path = os.path.join(PROJECT_ROOT, "backend", "database", "goals.db")
    
    plans_html = {}
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT area, goals FROM goals")
            rows = cursor.fetchall()
            for area, raw_md in rows:
                plans_html[area.lower()] = markdown.markdown(raw_md, extensions=['fenced_code', 'tables'])
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
            
    return render_template("goals.html", plans=plans_html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
