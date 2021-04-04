from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json
import copy


with open("secret.json") as f:
    SECRET = json.load(f)

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}".format(
    user=SECRET["user"],
    password=SECRET["password"],
    host=SECRET["host"],
    port=SECRET["port"],
    db=SECRET["db"])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Soldier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False)
    age = db.Column(db.Integer, unique=False)

    def __init__(self, name, age):
        self.name = name
        self.age = age


class SoldierSchema(ma.Schema):
    class Meta:
        fields = ('name', 'age')


soldier_schema = SoldierSchema()
soldiers_schema = SoldierSchema(many=True)


@app.route("/soldier", methods=["POST"])
def add_soldier():
    name = request.json['name']
    age = request.json['age']
    new_soldier = Soldier(name, age)
    db.session.add(new_soldier)
    db.session.commit()
    return soldier_schema.jsonify(new_soldier)


@app.route("/soldier", methods=["GET"])
def get_soldier():
    all_soldiers = Soldier.query.all()
    result = soldiers_schema.dump(all_soldiers)
    return jsonify({'soldiers_schema': result})


@app.route("/soldier/<id>", methods=["GET"])
def soldier_detail(id):
    soldier = Soldier.query.get(id)
    if not soldier:
        abort(404)
    return soldiers_schema.jsonify(soldier)


@app.route("/soldier/<id>", methods=["PUT"])
def soldier_update(id):
    soldier = Soldier.query.get(id)
    if not soldier:
        abort(404)
    old_soldier = copy.deepcopy(soldier)
    soldier.name = request.json['name']
    soldier.age = request.json['age']
    db.session.commit()
    return soldiers_schema.jsonify(soldier)


@app.route("/soldier/<id>", methods=["DELETE"])
def soldier_delete(id):
    soldier = Soldier.query.get(id)
    if not soldier:
        abort(404)
    db.session.delete(soldier)
    db.session.commit()
    return soldiers_schema.jsonify(soldier)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='127.0.0.1')

