import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''


# db_drop_and_create_all()

## ROUTES


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    drinks_short_formatted = [drink.short() for drink in drinks]

    return jsonify(
        {"success": True,
         "drinks": drinks_short_formatted}
    )


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks = Drink.query.all()
    drinks_long_formatted = [drink.long() for drink in drinks]

    return jsonify(
        {"success": True,
         "drinks": drinks_long_formatted}
    )


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    drink = request.get_json()
    title = drink["title"]
    recipe = json.dumps(drink['recipe'])

    new_drink = Drink(title=title, recipe=recipe)

    new_drink.insert()


    return jsonify(
        {"success": True,
         "drinks": [new_drink.long()]})


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)
    else:
        change = request.get_json()
        if change.get('title'):
            new_name = change.get('title')
            drink.title = new_name
        elif change.get('recipe'):
            changes = change.get('recipe')
            new_recipe = json.dumps(changes)
            drink.recipe = new_recipe

        drink.update()

        return jsonify(
            {"success": True,
             "drinks": [drink.long()]})


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)
    else:
        drink.delete()

    return jsonify(
        {"success": True,
         "delete": id})



@app.route('/login')
def login():
    return (request.args.get('access_token'))



@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def autherror_handler(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
