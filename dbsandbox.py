from pprint import pprint
from pymongo import MongoClient
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import time
#NOTE : Need this package for MongoClient init
#Without it, SSL CERTIFICATE VERIFY FAILED EXCEPTION
#Should find a better solution but i got fed up lol
import certifi
# import database

CONNECTION_STRING = "mongodb+srv://smartplugadmin:uodqp8ln7wOyKSMV@cluster0.gu6op.mongodb.net/SmartPlugDatabase?retryWrites=true&w=majority"


print("Doing sandbox stuff with database")

sched = BackgroundScheduler(daemon=True)

def myTask():
    print("Running scheduled task!")


sched.add_job(myTask,'cron',minute=7)

sched.start()

for i in range(0, 60):
    print("Waiting")
    time.sleep(1)
    
sched.shutdown()

exit()

client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())      #overhead setup
db = client.SmartPlugDatabase
userscollection = db.users
plugscollection = db.plugs
pricescollection = db.prices
