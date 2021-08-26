from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assortment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'mysecret'

db = SQLAlchemy(app)


@app.route('/')
def index():
    return "Is it visible?"


@app.route('/admin/add')
def add():
    return render_template('admin/add-product.html', admin=True)


if __name__ == '__main__':
    app.run()