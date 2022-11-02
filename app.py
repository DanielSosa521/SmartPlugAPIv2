__author__ = "Daniel Sosa"
__date__ = "April 14, 2022"

from datetime import datetime
import calendar
from email import message
import random
from pymongo import MongoClient
from pprint import pprint
import paho.mqtt.client as mqtt
import subprocess

#NOTE : Need this package for MongoClient init
#Without it, SSL CERTIFICATE VERIFY FAILED EXCEPTION
#Should find a better solution but i got fed up lol
import certifi
# import database

CONNECTION_STRING = "mongodb+srv://smartplugadmin:uodqp8ln7wOyKSMV@cluster0.gu6op.mongodb.net/SmartPlugDatabase?retryWrites=true&w=majority"



from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
# from marshmallow import Schema, fields


app = Flask(__name__)
api = Api(app)

# parser = reqparse.RequestParser()
# parser.add_argument('username', type="str")
# parser.add_argument('password', type="str")

buildversion = str(datetime.now().month) + str(datetime.now().day) 


mqttclient = mqtt.Client()

@app.route('/')
def hello_world():
    return 'Hello, World! API on Render now. API build code : Infinity ' + buildversion

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

class RegisterUser(Resource):
    def get(self):
        print("Connection successful")
        return "Connection successful", 200
    def post(self):
        print("Registering a user")
        jsondata = request.get_json(force=True)
        username = jsondata['username']
        password = jsondata['password']
        return "Register User", 200
api.add_resource(RegisterUser, "/register")

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
        script = "python pub.py"
        topic = "sosa/test"
        payload = "MQTT worked " + str(int(random.random()*10000))
        cmdline = script + " " + topic + " \"" + payload + "\""
        print(subprocess.getoutput(cmdline))
        return "Called " + script + "... Topic " + topic + " published : " + payload
api.add_resource(PlugRegistration, "/test/mqtt")

class Timestamp(Resource):
    def get(self):
        now = datetime.now()
        year = str(now.year)
        month = str(now.month)
        day = str(now.day)
        hour = str(now.hour)
        hour = hour - 5
        if (hour < 0):
            hour = hour + 24
        minute = str(now.minute)
        timestamp = year+"_"+month+"_"+day+"_"+hour+minute
        print("Timestamp : " + timestamp)
        
        return timestamp
api.add_resource(Timestamp, "/timestamp")

@app.route('/mqtt/<signal>')
def publishSignal(signal):
    script = "python pub.py"
    topic = "sosa/plug"
    payload = str(signal).upper()
    messageid = str(int(random.random()*10000))
    cmdline = script + " " + topic + " \"" + payload + "\""
    print(subprocess.getoutput(cmdline))
    return "CMDLINE : " + cmdline + "\n Message deployment ID = " + messageid

@app.route('/upload/<plugid>/<status>/<current>/<energy>')
def uploadData(plugid, status, current, energy):
        print("Upoading data to database")
        client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())          #Overhead setup
        db = client.SmartPlugDatabase
        plugscollection = db.plugs

        plug = plugscollection.find_one({'plugid' : int(plugid)})               #Get document for plug
        pprint(plug)
        if (plug == None):
            client.close()
            message = 'Plug with ID' + plugid + ' not found'                    #Abort if plug does not exist
            print(message)
            return message

        previousEnergy = plug['energy']
        newEnergy = previousEnergy + int(energy)                            #Calculate new total energy
        now = datetime.now().replace(second=0, microsecond=0)               #log current time
        
        plugscollection.update_one(
            {'plugid' : int(plugid) },
            {'$set' : {
                'status'        :   status.upper(),                     #Update database document with  new data
                'current'       :   int(current),
                'energy'        :   newEnergy,
                'lastmodified'  :   now
            }})

        client.close()
        return "Upload data : plugid=" + plugid + " status=" + status + " current=" + current + " energy=" + energy
