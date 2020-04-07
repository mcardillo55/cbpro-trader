from .models import *
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
engine = create_engine('sqlite:///../data.db')
Session = sessionmaker(bind=engine)

@app.route('/')
def hello_world():
    session = Session()
    res = []
    for result in session.query(Product).all():
        res.append(result.product_id)
    return jsonify(res)