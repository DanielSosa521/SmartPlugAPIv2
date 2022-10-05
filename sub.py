#A simple testing script for an MQTT sub to test the publisher ig idk

import paho.mqtt.client as mqtt

def onMessage(client, userdata, msg):
    print("Message received")
    print(msg.topic + ": " + msg.payload.decode())

client = mqtt.Client()
client.enable_logger()
client.on_message = onMessage

print("Running mqttsub test sub script...QOS=1")

# mqtthost = "broker.mqttdashboard.com"
# mqtthost = "mqtt.eclipseprojects.io"
mqtthost = "test.mosquitto.org"

if (client.connect(mqtthost, 1883, 30) != 0):
    print("Could not connect to " + mqtthost)
    exit()
else:
    print("Connection successful to " + mqtthost)

# mytopic = "sosa/test"
mytopic = "sosa/plug"
client.subscribe(mytopic, 1)
print("Subscribed to topic :" + mytopic)

try:
    print("Press Ctrl+C to exit...")
    client.loop_forever(1, retry_first_connection=True)
except:
    print("Disconnecting from broker")

client.disconnect()