#$env:FLASK_APP = "main" --> ${API}:FLASK_APP = "main"  
#API/Scripts/activate.bat
#from application import db
#flask run

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request

from flask import jsonify
from flask import make_response

import jwt
import datetime

from functools import wraps


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)




class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))

    def __repr__(self):
        return f"{self.name} - {self.description}"

@app.route('/')
def index():
    return 'Hello!'

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    output = []
    for drink in drinks:
        drink_data = {'name':drink.name, 'description': drink.description}
        output.append(drink_data)
    return {"drinks": output}

@app.route('/drinks/<id>')
def get_dring(id):
    drink = Drink.query.get_or_404(id)
    return {"name":drink.name, "description":drink.description}


@app.route('/drinks', methods=['POST'])
def add_drink():
    drink = Drink(name=request.json["name"], description=request.json["description"])
    db.session.add(drink)
    db.session.commit()
    return {'id':drink.id}

@app.route('/drinks/<id>', methods=['DELETE'])
def delete_drink(id):
    drink = Drink.query.get(id)
    if drink is None:
        return {"error":"not found"}
    db.session.delete(drink)
    db.session.commit()
    return {"message":"Deleted"}


@app.route('/login')
def login():
    auth = request.authorization

    if  auth and auth.password == 'password1':
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=5)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token})

    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return {'message' : 'Token is missing'}, 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            
        except:
            return {'message' : 'Token is invalid'}, 403

        return f(*args, **kwargs)
    return decorated
    
@app.route('/unprotected')
def unprotected():
    return  {'message' : 'Anyone can see this.'}



@app.route('/protected')

@token_required
def protected():
    return  {'message' : 'Availavle with valid tokens.'}


if __name__ == '__main__':
    app.run(debug=True)