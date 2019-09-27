from flask import Flask, request, jsonify, abort
from flask import render_template
from config import Config
app = Flask(__name__)
app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow # Order is important here!
db = SQLAlchemy(app)
ma = Marshmallow(app)

from models import Product
from schemas import products_schema, product_schema

@app.route('/')
def home():
    products = db.session.query(Product).all()
    return render_template('home.html', products=products)

@app.route('/<int:id>')
def product_html(id):
    product = db.session.query(Product).get(id)
    return render_template('product.html', product=product)

@app.route('/products')
def read_products():
    products = db.session.query(Product).all() # SQLAlchemy request => 'SELECT * FROM products'
    return products_schema.jsonify(products)

@app.route('/products/<int:id>')
def read_product(id):
    #query db
    to_return = db.session.query(Product).get(id)
    #serialize and return
    products_schema.jsonify(to_return)


@app.route('/products', methods=['POST'])
def create_product():
    #get json body
    json = request.get_json()
    #validate parameters in json
    if type(json) is dict:
        new_product = process_create_poduct(json)
        return product_schema.jsonify(new_product),201
    elif type(json) is list:
        #bulk create
        created_products = []
        for item in json:
            created_products.append(process_create_poduct(item))
        return products_schema.jsonify(created_products),201
    else:
        abort(422)

def process_create_poduct(json):
    # if not "name" -> 400

    if "name" in list(json) and json["name"] != None:
        desc = None
        if "description" in list(json):
            desc = json['description']

        # filtered_json = { key, value for key, value in json if key in ['name', 'description'] }
        # Product(**filtered_json)

        #create product object
        new_product = Product()
        #product = Product(**filtered_json)
        Product(name=json['name'], description=desc)
        #persist in db
        db.session.add(new_product)
        db.session.commit()
        return new_product

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    to_delete = db.session.query(Product).get(id)
    if to_delete != None:
        num_row = db.session.delete(to_delete)
        db.session.commit()
    return '', 204

@app.route('/products', methods=['DELETE'])
def bulk_delete_product():
    #get json list
    json = request.get_json()
    if "ids" in list(json) and type(json['ids']) is list:
        for id_to_delete in json['ids']:
            to_delete = db.session.query(Product).get(id_to_delete)
            if to_delete != None:
                num_row = db.session.delete(to_delete)
        db.session.commit()
        return '', 204
    else:
        abort(422)

@app.route('/products/<int:id>', methods=['PATCH'])
def update_product(id):
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
    return '', 204
