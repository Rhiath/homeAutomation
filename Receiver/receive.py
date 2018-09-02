#!/usr/bin/env python
#from __future__ import print_function
import time
import datetime
import sys
from RF24 import *
import RPi.GPIO as GPIO
from flask import Flask, request, make_response, Response
from flask_restful import Api, Resource
from json import dumps
#from flask.ext.jsonpify import jsonify
import threading
import urllib2
from xml.dom.minidom import parse
import xml.dom.minidom
import sensors
import building
import jsonpickle
import feeder
import htmlRenderer
 
# RPi Alternate, with SPIDEV - Note: Edit RF24/arch/BBB/spi.cpp and  set 'this->device = "/dev/spidev0.0";;' or as listed in /dev
radio = RF24(22, 0);
 
pipes = [0x314e6f6465]
payload_size = 32
millis = lambda: int(round(time.time() * 1000))
lastMeasurement = {}
lastConnectionToCC2 = 0

app = Flask(__name__)
api = Api(app)

def loadBuilding(fileName):
        document = xml.dom.minidom.parse(fileName)
        element = document.childNodes[0]

        return building.Building(element)

theBuilding = loadBuilding("building.xml")

class Api(Resource):
    def get(self):
	return Response(jsonpickle.encode(theBuilding, unpicklable=False), mimetype='application/json')

api.add_resource(Api, '/api')
api.add_resource(htmlRenderer.Renderer, '/status', resource_class_kwargs={"theBuilding": theBuilding})

radio.begin()
 
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1,pipes[0])

def getNodeID(message):
	return message.split(':')[0].decode("utf-8") 

def getTemperature(message):
	return message.split(":")[2].decode("utf-8").rstrip(' \t\r\n\0')

def getHumidity(message):
	return message.split(":")[1].decode("utf-8").rstrip(' \t\r\n\0')

def recordSensorMeasurement(nodeID, measurementType, measurementValue):
	if not (nodeID in lastMeasurement):
		lastMeasurement[nodeID] = {}
	formattedTimestamp = makePrettyTimestamp(time.time())
	lastMeasurement[nodeID][measurementType] = (measurementValue, formattedTimestamp)

def makePrettyTimestamp(timestamp):
	retValue = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
	return retValue


def handleMessage(message):
	nodeID = getNodeID(message)
	humidity = getHumidity(message)
	temperature = getTemperature(message)

#	print(nodeID+" --> "+humidity+" RH, "+temperature+" C")
	values = {}
	values["T"] = temperature
	values["H"] = humidity
	recordSensorMeasurement(nodeID, "DHT22", values)	

def getDeviceType(devices, deviceName):	
	for device in devices.childNodes[0].childNodes :
#		print(device.getAttribute("name")+" vs. "+deviceName)
		if (device.getAttribute("name") == deviceName ):
			return device.getAttribute("device_type")
	return "unknown";

def getDomainSensorValue(deviceType, sensorType, value):
	if (deviceType == "HM-Sec-SC-2" and sensorType == "STATE"):
		if ( value == "true"): value = "OPEN"
		if ( value == "false"): value = "CLOSED"

	if (deviceType == "HM-Sec-RHS" and sensorType == "STATE"):
		if ( value == "0"): value = "LOCK"
		if ( value == "1"): value = "TILT"
		if ( value == "2"): value = "UNLOCK"


	return value;

def startRESTService():
    app.run(port='5002', host= '0.0.0.0')
 
if __name__ == "__main__":
    thread = threading.Thread(target=startRESTService)
    thread.daemon = True
    thread.start()
    print("started REST service")

    thread2 = threading.Thread(target=feeder.keepFeedingFromCC2(theBuilding, 5.0, "homematic-cc2"))
    thread2.daemon = True
    thread2.start()
    print("started CC2 grabber")


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

