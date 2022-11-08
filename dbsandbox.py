from pprint import pprint
from pymongo import MongoClient
from datetime import datetime
import pytz
#NOTE : Need this package for MongoClient init
#Without it, SSL CERTIFICATE VERIFY FAILED EXCEPTION
#Should find a better solution but i got fed up lol
import certifi
# import database

CONNECTION_STRING = "mongodb+srv://smartplugadmin:uodqp8ln7wOyKSMV@cluster0.gu6op.mongodb.net/SmartPlugDatabase?retryWrites=true&w=majority"


print("Doing sandbox stuff with database")
austinTimeZone = pytz.timezone('America/Chicago')
timeInAustin = datetime.now(austinTimeZone)
print(timeInAustin.strftime("%H:%M:%S"))
exit()

client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())      #overhead setup
db = client.SmartPlugDatabase
userscollection = db.users
plugscollection = db.plugs
pricescollection = db.prices


dayNumeric = ( datetime.today().weekday() + 1 ) % 7
print(dayNumeric)

daypricedata = pricescollection.find_one({
    'day' : dayNumeric
})

# pprint(daypricedata)

hourlyPrices = daypricedata['priceValues']

print(hourlyPrices)

currentHour = datetime.now().hour
# currentHour = currentHour - 5
# if (currentHour < 0):
#     currentHour = currentHour + 24
print(currentHour)

currentPrice = hourlyPrices[currentHour]

print("Current price : " + str(currentPrice))
foresightRange = min(currentHour+7, 24)
cheaperAvailable = False

for i in range (currentHour+1, foresightRange):
    if (hourlyPrices[i] < (currentPrice * .75)):
        cheaperAvailable = True
        print("Power cheaper at " + str(i) + " for cost of " + str(hourlyPrices[i]))

print("Confirm?" if cheaperAvailable else "Pricing OK")