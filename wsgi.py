from flask import Flask
from config import Config
app = Flask(__name__)
app.config.from_object(Config)


from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow # Order is important here!
db = SQLAlchemy(app)
ma = Marshmallow(app)
from models import Product
from schemas import products_schema

@app.route('/hello')
def hello():
    return "Hello World!"

@app.route('/products')
def products():
    products = db.session.query(Product).all() # SQLAlchemy request => 'SELECT * FROM products'
    return products_schema.jsonify(products)

@app.route('/products/<int:id>')
def getOneProduct(id):
    #query db
    to_return = db.session.query(Product).get(id)
    #serialize and return
    products_schema.jsonify(to_return)


@app.route('/products', methods=['POST'])
def create_product():
    #get json body
    json = request.get_json()
    #validate parameters in json
    if "name" in list(json) and json["name"] != None:
        #create product object
        new_product = Product()
        new_product.name = json["name"]
        #persist in db
        db.session.add(new_product)
        db.session.commit()

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_object(id):
    num_row = db.session.query(Product).get(id).delete()
    db.session.commit()
    return jsonify(num_row)

@app.route('/products/<int:id>', methods=['PATCH'])
def change_object(id):
    #get json with modifs
    json = request.get_json()
    modified_product = db.session.query(Product).get(id)
    #change object based on json
    if "name" in list(json):
        modified_product.name = json['name']
    if "description" in list(json):
        modified_product.description = json["description"]
    #persist in db
    db.session.add(modified_product)
    db.session.commit()
