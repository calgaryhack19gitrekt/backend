from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'main.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('username', 'email')

class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Integer)
    latitude = db.Column(db.Integer)
    available = db.Column(db.Boolean)

    def __init__(self,longitude,latitude,available):
        self.id = id
        self.longitude = longitude
        self.latitude = latitude
        assert(type(available) is bool)
        self.available = available

class BikeSchema(ma.Schema):
    class Meta:
        fields = ('longitude','latitude','available')

#init schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)

bike_schema = BikeSchema()
bikes_schema = BikeSchema(many=True)

#Bike methods
@app.route("/allbikes", methods=["GET"])
def get_all_bikes():
    all_bikes = Bike.query.all()
    result = bike_schema.dump(all_bikes)
    return jsonify(result.data)

@app.route('/bike/<available>', methods=["GET"])
def get_free_bikes(available):
    bikes = Bike.query.filter_by(available=available)
    return bike_schema.jsonify(bikes)

@app.route("/bike/<id>", methods=["GET"])
def bike_detail(id):
    bike = Bike.query.get(id)
    return bike_schema.jsonify(bike)

@app.route("/bike/<id>", methods=["PUT"])
def set_to_busy(id):
    bike = Bike.query.get(id)

    available = request.json['available']
    bike.available = available

    db.session.commit()
    return bike_schema.jsonify(bike)

# endpoint to create new user
@app.route("/user", methods=["POST"])
def add_user():
    username = request.json['username']
    email = request.json['email']
    
    new_user = User(username, email)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user)


# endpoint to show all users
@app.route("/user", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)


# endpoint to get user detail by id
@app.route("/user/<id>", methods=["GET"])
def user_detail(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)


# endpoint to update user
@app.route("/user/<id>", methods=["PUT"])
def user_update(id):
    user = User.query.get(id)
    username = request.json['username']
    email = request.json['email']

    user.email = email
    user.username = username

    db.session.commit()
    return user_schema.jsonify(user)


# endpoint to delete user
@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)


if __name__ == '__main__':
    app.run(debug=True)

