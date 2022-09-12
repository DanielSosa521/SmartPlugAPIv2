__author__ = "Daniel Sosa"
__date__ = "April 14, 2022"

from datetime import datetime
import calendar
import random
from pymongo import MongoClient
import paho.mqtt.client as mqtt

#NOTE : Need this package for MongoClient init
#Without it, SSL CERTIFICATE VERIFY FAILED EXCEPTION
#Should find a better solution but i got fed up lol
import certifi
# import database

CONNECTION_STRING = "mongodb+srv://smartplugadmin:uodqp8ln7wOyKSMV@cluster0.gu6op.mongodb.net/SmartPlugDatabase?retryWrites=true&w=majority"



from flask import Flask, jsonify, request
from flask_restful import Api, Resource
app = Flask(__name__)
api = Api(app)

buildversion = str(datetime.now().month) + str(datetime.now().day) 

@app.route('/')
def hello_world():
    return 'Hello, World! API on Render now. API build code : Dwarf ' + buildversion

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

class DashboardMonth(Resource):
    def get(self):
        print("Providing Month Data\n")
        points = []
        samples = datetime.now().day        #Samples = day of month
        for day in range(samples):
            pwr = random.randint(400,800)
            points.append(day)
            points.append(pwr)
        print(points)
        return {
            'points':points
        }
api.add_resource(DashboardMonth, "/dashboard/month")

class DashboardDay(Resource):
    def get(self):
        print("Providing Day Data\n")
        points = []
        samples = datetime.now().hour       #Samples = current hour in 24 hour format (noon = 12, 5 pm = 17)
        for day in range(samples):
            pwr = random.randint(0,25)
            points.append(day)
            points.append(pwr)
        print(points)
        return {
            'points':points
        }
api.add_resource(DashboardDay, "/dashboard/day")

class DashboardPlugs(Resource):
    def get(self):
        print("Providing plug data\n")
        plugCount = 4                           #Hardcoding 4 plugs for testing
        points = []
        for plug in range(plugCount):
            plugPower = random.randint(0,15)        #Each plug = random power from 0 to 15
            points.append(plug)
            points.append(plugPower)
        print(points)
        return {
            'points' : points
        }
api.add_resource(DashboardPlugs, "/dashboard/plugs")

class Database(Resource):
    def get(self):
        print("Displaying database information")
        client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
        db = client.SmartPlugDatabase
        userscollection = db.users
        plugscollection = db.plugs
        print ("Collections:\n")
        collections = []
        for c in db.list_collection_names():
            collections.append(c)                       #Add collection name to list
            # coll = db[c]      //access that collection
        users = []
        cursor = userscollection.find({})
        for u in cursor:
            users.append(str(u))
        plugs = []
        cursor = plugscollection.find({})
        for p in cursor:
            plugs.append(str(p))
        return {
            'collections' : collections,
            'users' : users,
            'plugs' : plugs
        }
api.add_resource(Database, "/database")

class PlugRegistration(Resource):
    def get(self):
        print("Doing mqtt testing")
        client = mqtt.Client()
        mqtthost = "broker.mqttdashboard.com"  
        if (client.connect(mqtthost, 1883, 30) != 0):
            return "Could not connect to MQTT server"
        else:
            status = "MQTT Server connection successful"
            mytopic = "sosa/test"
            mypayload = "sosa api mqtt message"
            print("Publishing test message to " + mqtthost + "::" + mytopic)
            client.publish(topic=mytopic, payload=mypayload, qos=2)
            return status
api.add_resource(PlugRegistration, "/test/mqtt")