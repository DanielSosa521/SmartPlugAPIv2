__author__ = "Daniel Sosa"
__date__ = "April 14, 2022"

from datetime import datetime
import calendar
import random
from pymongo import MongoClient

#NOTE : Need this package for MongoClient init
#Without it, SSL CERTIFICATE VERIFY FAILED EXCEPTION
#Should find a better solution but i got fed up lol
# import certifi
# import database

from flask import Flask, jsonify
from flask_restful import Api, Resource
app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello_world():
    return 'Hello, World! API on Render now. API build code : Astronaut'

class Home(Resource):
    def get(self):
        currentMonth = datetime.now().month
        month = calendar.month_name[currentMonth]
        summary = "Energy usage looks good"
        moneysaved = random.randint(-200,200)
        powersaved = moneysaved * 27
        savings = "$"+str(moneysaved)+" : "+str(powersaved)+"KWH"
        delta = random.randint(-15,20)
        plugs = ["plug1","plug2","plug4"]
        return {
            'month':month,
            'summary':summary,
            'savings':savings,
            'delta':delta,
            'plugs':plugs
        }
api.add_resource(Home, "/home")
