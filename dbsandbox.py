from pprint import pprint
from pymongo import MongoClient
from datetime import datetime
#NOTE : Need this package for MongoClient init
#Without it, SSL CERTIFICATE VERIFY FAILED EXCEPTION
#Should find a better solution but i got fed up lol
import certifi
# import database

CONNECTION_STRING = "mongodb+srv://smartplugadmin:uodqp8ln7wOyKSMV@cluster0.gu6op.mongodb.net/SmartPlugDatabase?retryWrites=true&w=majority"


print("Doing sandbox stuff with database")

client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())      #overhead setup
db = client.SmartPlugDatabase
userscollection = db.users
plugscollection = db.plugs


user = userscollection.find_one({'username':'danielsosa'})      #find user with username danielsosa
pprint(user)

userplugs = user['plugs']                               #list user's registered plugs

print("User has plugs " + str(userplugs))

for p in userplugs:                                             #for each plug
    print("Searching database for plug " + str(p))
    plug = plugscollection.find_one({'plugid' : p})                     #find each plugs db document
    pprint(plug)
    now = datetime.now().replace(second=0, microsecond=0)               #log current time
    print(now)
    plugscollection.update_one(
        {'plugid' : p},                                                 #update document for plug = plugid
        {'$set' : {
            'status'        :   'ON'.upper(),                           #set status
            'lastmodified'  :   now                                     #set lastmodified info
         }})    #update database document

# users = []
# cursor = userscollection.find({})
# for u in cursor:
#     users.append(str(u))
# plugs = []
# cursor = plugscollection.find({})
# for p in cursor:
#     plugs.append(str(p))
# print(users)
# print(plugs)