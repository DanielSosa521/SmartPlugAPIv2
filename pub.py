#A simple testing script for an MQTT sub to test the publisher ig idk

import paho.mqtt.client as mqtt
import sys, os

client = mqtt.Client()

print("cmdargs : " + str(sys.argv))
print("progname = " + os.path.basename(__file__))   #Get cmd line info

if (len(sys.argv) != 3):
    print("ERROR : Usage : ./pub <topic> <payload>")    ##ensure topic and payload provided
    exit()

mqtthost = "broker.mqttdashboard.com"                   #Broker URL

if (client.connect(mqtthost, 1883, 30) != 0):
    print("Could not connect to " + mqtthost)       #Setup connection to broker
    exit()
else:
    print("Connection successful at " + mqtthost)

mytopic = "sosa/test"
mytopic = sys.argv[1]                       #Read topic name from cmdline
print("Topic : " + mytopic)

mypayload = "default pub message"
mypayload = sys.argv[2]                     #Read payload from cmdline
print("Payload = " + mypayload)

myqos = 1
print("QOS = " + str(myqos))                     #QOS = at least once ( 1 )

client.publish(mytopic, mypayload, myqos)       #Publish message

client.disconnect()                         #Disconnect from broker