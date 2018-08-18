#!/usr/bin/env python
#from __future__ import print_function
import time
import datetime
import sys
from RF24 import *
import RPi.GPIO as GPIO
from flask import Flask, request
from flask_restful import Api, Resource
from json import dumps
#from flask.ext.jsonpify import jsonify
import threading
 
# RPi Alternate, with SPIDEV - Note: Edit RF24/arch/BBB/spi.cpp and  set 'this->device = "/dev/spidev0.0";;' or as listed in /dev
radio = RF24(22, 0);
 
pipes = [0x314e6f6465]
payload_size = 32
millis = lambda: int(round(time.time() * 1000))
lastMeasurement = {}

app = Flask(__name__)
api = Api(app)

class Sensors(Resource):
    def get(self):
        return lastMeasurement


api.add_resource(Sensors, '/sensors')

radio.begin()
 
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1,pipes[0])

def getNodeID(message):
	return message.split(':')[0].decode("utf-8") 

def getType(message):
	return chr(message.split(':')[1][0])

def getValue(message):
	return message.split(":")[1][1:].decode("utf-8").rstrip(' \t\r\n\0')

def handleMessage(message):
	nodeID = getNodeID(message)
	measurementType = getType(message)
	measurementValue = getValue(message)

	if ( measurementType == "T" ):
		measurementValue = measurementValue + u" \u00b0C"
	if ( measurementType == "H" ):
		measurementValue = measurementValue + "% RH"


	if not (nodeID in lastMeasurement):
		lastMeasurement[nodeID] = {}
	
	formattedTimestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%M:%S')
	lastMeasurement[nodeID][measurementType] = (measurementValue, formattedTimestamp)

def startRESTService():
    app.run(port='5002', host= '0.0.0.0')
 
if __name__ == "__main__":
    thread = threading.Thread(target=startRESTService)
    thread.daemon = True
    thread.start()
    print("started REST service")


    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    radio.startListening()

    while True:
	timeout = False
	started_waiting_at = millis()
	while (not radio.available()) and (not timeout):
        	if (millis() - started_waiting_at) > 500:
	            timeout = True

	if timeout:
		time.sleep(0.1)
	else:
        	# Grab the response, compare, and send to debugging spew
	        len = radio.getDynamicPayloadSize()
        	receive_payload = radio.read(len)
		handleMessage(receive_payload)
		print(lastMeasurement)

