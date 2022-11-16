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
import pytz
from apscheduler.schedulers.background import BackgroundScheduler


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
def getAustinDatetimeNow():
    austinTimeZone = pytz.timezone('America/Chicago')
    timeInAustin = datetime.now(austinTimeZone)
    return timeInAustin
    
buildLabel = 'Lunar'
buildversion = str(getAustinDatetimeNow().month) + str(getAustinDatetimeNow().day)      #Tracker for monitoring build version

costSavingHours = {}            #Global dictionary for alternative cost saving power use hours

sched = BackgroundScheduler(timezone='America/Chicago', daemon=True)        #Scheduler object

mqttclient = mqtt.Client()              #MQTT Broker client


@app.route('/')
def hello_world():
    return 'Hello, World! API on Render now. API build code : ' + buildLabel + ' ' + buildversion

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
        now = getAustinDatetimeNow()
        year = str(now.year)
        month = str(now.month)
        day = str(now.day)
        hour = now.hour
        if (hour < 0):
            hour = hour + 24
        if (hour < 10):
            hour = '0' + str(hour)
        else :
            hour = str(hour)
        minute = now.minute
        if (minute < 10):
            minute = '0' + str(minute)
        else:
            minute = str(minute)
        timestamp = year+"_"+month+"_"+day+"_"+hour+minute
        print("Timestamp : " + timestamp)
        
        return timestamp
api.add_resource(Timestamp, "/timestamp")


# publishDirect
# Publishes a message without any verification, used for scheduled jobs
def publishDirect(signal):
    print("Doing scheduled publishDirect at " + str(getAustinDatetimeNow()))
    script = "python pub.py"
    topic = "sosa/plug"
    payload = signal
    messageid = str(int(random.random()*10000))
    cmdline = script + " " + topic + " \"" + payload + "\""
    print(subprocess.getoutput(cmdline))
    print('MessageID : ' + str(messageid))


@app.route('/schedule/<signal>/<hour>/<minute>')
def scheduleSignal(signal, hour, minute):
    hrInt = int(hour)
    minInt = int(minute)
    if (hrInt < 0 or hrInt > 23 or minInt < 0 or minInt > 59):      #Check for valid time
        return "ERROR : Invalid time input"

    signal = str(signal).upper()
    if (not (signal == 'ON' or signal == 'OFF')):                       #Check for valid signal type (ON or OFF)
        return "ERROR : Invalid signal type"

    prompt = "Scheduling auto " + signal + " at " + hour+':'+minute
    print(prompt)
    sched.add_job(  publishDirect,                      #Add job to scheduler with specified signal, hour, minute
                    'cron',
                    args=[signal],       
                    hour=hrInt, 
                    minute=minInt)
    
    return prompt

@app.route('/schedule/startscheduler')
def startScheduler():
    sched.start()
    return 'Scheduler started'

@app.route('/schedule/jobs')
def viewJobs():
    jobInfo = ''
    for job in sched.get_jobs():
        jobInfo = jobInfo+("name: %s, trigger: %s, next run: %s" % (        #Append job data
            job.name, job.trigger, job.next_run_time))
        jobInfo = jobInfo+'<br>'
    print(jobInfo)
    return jobInfo

@app.route('/schedule/clear')
def clearJobs():
    for job in sched.get_jobs():        #For every scheduled job
        job.remove()                        #Remove it
    prompt = 'Removed all jobs'
    print(prompt)
    return prompt

@app.route('/mqtt/<signal>')
def publishSignal(signal):
    script = "python pub.py"
    topic = "sosa/plug"
    payload = str(signal).upper()

    if (payload == 'ON'):
        if (powerExpensiveNow()):
            print("Power cost high")
            print("Cost Saving Hours - Hour : Price")
            print(costSavingHours)
            print("Need confirmation")
            return "confirm?"
        else:
            print("Power cost low, publishing signal")
    
    if (payload == 'CONFIRM'):
        payload = 'ON'

    messageid = str(int(random.random()*10000))
    cmdline = script + " " + topic + " \"" + payload + "\""
    print(subprocess.getoutput(cmdline))
    prompt = "CMDLINE : " + cmdline + "\n Message deployment ID = " + messageid
    return "published"


def powerExpensiveNow():
    print("Checking if power expensive right now")
    client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())      #Database overhead
    db = client.SmartPlugDatabase
    pricescollection = db.prices

    dayNumeric = ( datetime.today().weekday() + 1 ) % 7
    print("Today numeric : " + str(dayNumeric))
    daypricedata = pricescollection.find_one({                  #Get todays document
        'day' : dayNumeric
    })


    hourlyPrices = daypricedata['priceValues']
    print(hourlyPrices)
    currentHour = getAustinDatetimeNow().hour
    currentHour = currentHour
    if (currentHour < 0):
        currentHour = currentHour + 24                        #Get price of power at this hour
    print("Current hour : " + str(currentHour))
    currentPrice = hourlyPrices[currentHour]
    print("Current price : " + str(currentPrice))

    findCheaperHours(currentHour, currentPrice, hourlyPrices)       #Find hours when power is cheaper, store in global var

    return currentPrice >= 6

def findCheaperHours(currentHour, currentPrice, hourlyPrices):
    print("Running price checking algorithms to find better hours")
    global costSavingHours 

    foresightRange = min(currentHour+7, 24)                                     #Consider next 6 hours limited by midnight
    for i in range (currentHour+1, foresightRange):
        if (hourlyPrices[i] < (currentPrice * .75)):
            print("Power cheaper at " + str(i) + " for cost of " + str(hourlyPrices[i]))    
            costSavingHours[i] = hourlyPrices[i]                                            #Add hour:cost entry to global dict

lastUpload = ''

@app.route('/upload/<plugid>/<status>/<power>/')
def uploadData(plugid, status, power):
        print("Upoading data to database")
        client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())          #Overhead setup
        db = client.SmartPlugDatabase
        plugscollection = db.plugs

        plug = plugscollection.find_one({'plugid' : int(plugid)})               #Get document for plug
        if (plug == None):
            client.close()
            message = 'Plug with ID' + plugid + ' not found'                    #Abort if plug does not exist
            print(message)
            return message
        
        pprint(plug)

        now = getAustinDatetimeNow().replace(second=0, microsecond=0)               #log current time
        
        plugscollection.update_one(
            {'plugid' : int(plugid) },
            {'$set' : {
                'status'        :   status.upper(),                     #Update database document with  new data
                'power'         :   float(power),
                'lastmodified'  :   now
            }})

        client.close()

        global lastUpload
        lastUpload = "Last data upload : <br>Plug : " + plugid + "<br>Status : " + status + "<br>Power = " + power + "<br> at time : " + str(getAustinDatetimeNow().replace(microsecond=0))

        return "Upload success : plugid=" + plugid + " status=" + status + " power " + power

@app.route('/check')
def checkLastUpload():
    return lastUpload




