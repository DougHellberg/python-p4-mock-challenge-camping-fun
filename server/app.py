#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class CamperList(Resource):
    def get(self):
        campers = Camper.query.all()
        camper_dict = [camper.to_dict(rules=("-signups",))for camper in campers]
        return make_response(camper_dict, 200)
    
    def post(self):
        data=request.json
        try:
            camper = Camper(
                name = data['name'],
                age = data['age']
            )
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(rules = ('-signups',)),201)
        except ValueError:
            return make_response({ "errors": ["validation errors"] },400)
api.add_resource(CamperList,"/campers")

class CamperById(Resource):
    def get(self,id):
        camper = Camper.query.filter(Camper.id == id).first()
        if not camper:
            return make_response({"error":"Camper not found"},404)
        camper_to_dict = camper.to_dict()
        return make_response(camper_to_dict,200)
    
    def patch(self,id):
        camper = Camper.query.filter_by(id=id).first()
        if camper is not None:
            try:
                for attr in request.json:
                    setattr(camper,attr,request.json[attr])
                db.session.add(camper)
                db.session.commit()
                camper_to_dict = camper.to_dict()
                return make_response(camper_to_dict,202)
            except ValueError:
                return make_response({ "errors": ["validation errors"] },400)
        else:
            return make_response({"error":"Camper not found"},404)
            
            
api.add_resource(CamperById,"/campers/<int:id>")

class ActivityList(Resource):
    def get(self):
        activities = Activity.query.all()
        activity_dict = [activity.to_dict(rules=("-signups",))for activity in activities]
        return make_response(activity_dict, 200)
    
api.add_resource(ActivityList,"/activities")

class ActivityById(Resource):
    def delete(self,id):
        activity = Activity.query.filter_by(id=id).first()
        if activity is None:
            return make_response({"error": "Activity not found"},404)
        db.session.delete(activity)
        db.session.commit()
        return make_response({},204)

api.add_resource(ActivityById,"/activities/<int:id>")

class SignupList(Resource):
    def post(self):
        data = request.json
        try:
            signup = Signup(
                time = data['time'],
                activity_id = data['activity_id'],
                camper_id = data['camper_id']
            )
            db.session.add(signup)
            db.session.commit()
            return make_response(signup.to_dict(),201)
        except ValueError:
            return make_response({ "errors": ["validation errors"] },400)
api.add_resource(SignupList,"/signups")



if __name__ == '__main__':
    app.run(port=5555, debug=True)
