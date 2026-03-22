from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

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

# Ensure tables exist (safe to run even if they already exist)
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    print("DB PATH:", app.config["SQLALCHEMY_DATABASE_URI"])
    rows = Overview.query.all()
    print("ROW COUNT:", len(rows))  # CHECK how many rows fetched
    return render_template("layout.html", rows=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

