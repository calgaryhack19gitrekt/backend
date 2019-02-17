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
    firstName = db.Column(db.String(80), unique=False)
    lastName = db.Column(db.String(80), unique=False)
    phoneNum = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(120), unique=True)

    bikes = db.relationship('Bike', backref='user',lazy=True)

    def __init__(self, firstName, lastName, phoneNum, email):
        self.firstName = firstName
        self.lastName = lastName
        self.phoneNum = phoneNum
        self.email = email

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'firstName', 'lastName', 'phoneNum', 'email')


class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Integer)
    latitude = db.Column(db.Integer)
    available = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __init__(self,longitude,latitude):
        self.longitude = longitude
        self.latitude = latitude
        self.available = True
        self.user_id = -1

class BikeSchema(ma.Schema):
    class Meta:
        fields = ('id','longitude','latitude','available', 'user_id')
        print(fields)

#init schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)

bike_schema = BikeSchema(strict=True)
bikes_schema = BikeSchema(many=True, strict=True)


# endpoint to create new user
@app.route("/user/", methods=["POST"])
def add_user():
    firstName = request.json['firstName']
    lastName = request.json['lastName']
    phoneNum = request.json['phoneNum']
    email = request.json['email']
    
    new_user = User(firstName, lastName, phoneNum, email)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)


# endpoint to show all users
@app.route("/user/", methods=["GET"])
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

    firstName = request.json['firstName']
    lastName = request.json['lastName']
    phoneNum = request.json['phoneNum']
    email = request.json['email']

    user.firstName = firstName
    user.lastName = lastName
    user.phoneNum = phoneNum
    user.email = email

    db.session.commit()
    return user_schema.jsonify(user)


# endpoint to delete user
@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)

#Bike methods
@app.route("/bike/", methods=["POST"])
def add_bike():
    longitude = request.json['longitude']
    latitude = request.json['latitude']

    new_bike = Bike(longitude,latitude)
    
    db.session.add(new_bike)
    db.session.commit()
    
    return bike_schema.jsonify(new_bike)


# endpoint to show all bikes
@app.route("/bike/", methods=["GET"])
def get_bikes():
    all_bikes = Bike.query.all()
    result = bikes_schema.dump(all_bikes)
    return jsonify(result.data)

@app.route("/bike/<id>",methods=["GET"])
def bike_detail(id):
    bike = Bike.query.get(id)
    return bike_schema.jsonify(bike)


#def sort_bikes(bikes_list):



@app.route("/bike/avail/<available>", methods=["GET"])
def get_bike(available):
    bikes = Bike.query.filter_by(available=available).all()
    result = bikes_schema.dump(bikes)

    avail_bikes = result.data
    print(result.data)

    return jsonify(result.data)


@app.route("/bike/<id>", methods=["PUT"])
def change_status(id):
    bike = Bike.query.get(id)

    available = request.json['available']
    user_id = request.json['user_id']

    bike.available = available
    bike.user_id = user_id

    db.session.commit()
    return bike_schema.jsonify(bike)


if __name__ == '__main__':
    app.run(debug=True)

