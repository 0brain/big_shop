from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField
from flask_wtf.file import FileField, FileAllowed

from flask_uploads import UploadSet, configure_uploads, IMAGES  # pip install Flask-Reuploaded

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assortment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'mysecret'

configure_uploads(app, photos)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Integer) #in cents
    stock = db.Column(db.Integer)
    description = db.Column(db.String(500))
    image = db.Column(db.String(100))


class AddProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')
    stock = IntegerField('Stock')
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])


class AddToCart(FlaskForm):
    quantity = IntegerField("Quantity")
    id = HiddenField("ID")


@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/product/<id>')
def product(id):
    product = Product.query.filter_by(id=id).first()
    form = AddToCart()

    return render_template("view-product.html", product=product, form=form)


@app.route('/quick-add/<id>', methods=["GET"])
def quick_add(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({"id": id, 'quantity': 1})
    session.modified = True

    return redirect(url_for('index'))


@app.route('/add-to-cart', methods=["POST"])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    form = AddToCart()

    if form.validate_on_submit():

        session['cart'].append({"id": form.id.data, 'quantity': form.quantity.data})
        session.modified = True

    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    products = []

    for item in session["cart"]:
        product = Product.query.filter_by(id=item["id"]).first()

        quantity = int(item['quantity'])
        total = quantity * product.price
        products.append({'id': product.id, "name": product.name, "price": product.price, "image": product.image, 'quantity': quantity, 'total': total})
    return render_template("cart.html", products=products)


@app.route('/admin')
def admin():
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()
    return render_template('admin/index.html', admin=True, products=products, products_in_stock=products_in_stock)


@app.route('/admin/add', methods=['GET', 'POST'])
def add():
    form = AddProduct()

    if form.validate_on_submit():
        image_url = url_for("static", filename=f"img/{photos.save(form.image.data)}")

        new_product = Product(name=form.name.data, price=form.price.data, stock=form.stock.data, description=form.description.data, image=image_url)

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for("add"))

    return render_template('admin/add-product.html', admin=True, form=form)


if __name__ == '__main__':
    app.run()