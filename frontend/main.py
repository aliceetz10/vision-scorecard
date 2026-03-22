from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd

app = Flask(__name__)

# Connect to overview.db in the same directory as this file
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "overview.db")
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

# Model matching the existing 'overview' table
class Overview(db.Model):
    __tablename__ = "overview"
    id = db.Column(db.Integer, primary_key=True)
    field = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return self.field, self.analysis

class employment(db.Model):
    __tablename__ = "employment"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)
    is_employment = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return self.status, self.analysis, self.is_employment

def fetch_employment():
    employed = []
    unemployed = []
    rows = employment.query.all()
    for row in rows:
        if row.is_employment == 0:
            unemployed.append(row)
        else:
            employed.append(row)
    return employed, unemployed

# Ensure tables exist (safe to run even if they already exist)
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    print("DB PATH:", app.config["SQLALCHEMY_DATABASE_URI"])
    rows = Overview.query.all()
    print("ROW COUNT:", len(rows))

    employment, unemployment = fetch_employment()

    return render_template("index.html", rows=rows, unemployment=unemployment, employment=employment)

@app.route("/goals")
def goals():
    # Setup paths relative to this script's directory (frontend/)
    # We need to go up to project root, then into backend/data/processed
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(base_dir, "backend", "data", "processed")
    
    plans = {}
    filenames = {
        "waterloo": "Waterloo_Strategic_Plan_2023-2026.txt",
        "kitchener": "Kitchener_Strategic_Plan_2023-2026.txt",
        "cambridge": "Cambridge_Strategic_Plan_2024-2026.txt"
    }
    
    for key, filename in filenames.items():
        path = os.path.join(processed_dir, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                plans[key] = f.read()
        else:
            plans[key] = "Data currently unavailable."
            
    return render_template("goals.html", plans=plans)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
