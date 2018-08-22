#!/usr/bin/env python
#from __future__ import print_function
import time
import datetime
import sys
from RF24 import *
import RPi.GPIO as GPIO
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from json import dumps
#from flask.ext.jsonpify import jsonify
import threading
import urllib
from xml.dom.minidom import parse
import xml.dom.minidom
import sensors
import building
 
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

class Status(Resource):
    @staticmethod
    def getChildren(element, name):
	retValue = []
	for child in element.childNodes:
		if ( child.nodeName == name ):
			retValue.append(child)
	return retValue

    @staticmethod
    def renderSensors(element):
	retValue = "";
	values = []
	for sensor in Status.getChildren(element, "sensor"):
		name = sensor.getAttribute("name")
		value = Status.renderSensorValue(sensor)
		sens = sensors.Sensor(value)
		values.append(sens)
	multi = sensors.MultiSensor(values)
	return multi.toHTML()

    @staticmethod
    def renderSensorValue(element):
	name = element.getAttribute("name")
	retValue = "unknown"
	if ( name in lastMeasurement):
		sensor = lastMeasurement[name]
		sensorType = next(iter(sensor))
		retValue = sensor[sensorType][0]["STATE"]

	if ( retValue == "OPEN" or retValue == "UNLOCK" ):
		retValue = "<font color=\"red\">"+retValue+"</font>"

	if ( retValue == "TILT" ):
		retValue = "<font color=\"GoldenRod\">"+retValue+"</font>"

	if ( retValue == "CLOSED" or retValue == "LOCK" ):
		retValue = "<font color=\"green\">"+retValue+"</font>"

	return retValue;

    @staticmethod
    def renderRoom(room):
	retValue = "";
	retValue = retValue + "<h2>" + room.getAttribute("name") + "</h2>"
	retValue = retValue + Status.renderSensors(room)
	for door in Status.getChildren(room, "door"):
		retValue = retValue + Status.renderDoor(door)
	for window in Status.getChildren(room, "window"):
		retValue = retValue + Status.renderWindow(window)
	return retValue

    @staticmethod
    def renderDoor(element):
	return "<b>"+element.getAttribute("name")+" [" + Status.renderSensors(element)+"]</b><br />"

    @staticmethod
    def renderWindow(element):
	return "<b>"+element.getAttribute("name")+" [" + Status.renderSensors(element)+"]</b><br />"


    def get(self):
        retValue = "<html><head><meta http-equiv=\"refresh\" content=\"5\"></head><body>"
	

	building = xml.dom.minidom.parse("building.xml")
	for floor in Status.getChildren(building.childNodes[0],"floor"):
		retValue = retValue + "<h1>" + floor.getAttribute("name") + "</h1>"
		for hallway in Status.getChildren(floor, "hallway"):
			for door in Status.getChildren(hallway, "door"):
				retValue = retValue + Status.renderDoor(door)
		for room in Status.getChildren(floor, "room"):
			retValue = retValue + Status.renderRoom(room)

	retValue = retValue + "</body></html>"
	return make_response(retValue, 200)

api.add_resource(Sensors, '/sensors')
api.add_resource(Status, '/status')

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
	
	formattedTimestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%M:%S')
	lastMeasurement[nodeID][measurementType] = (measurementValue, formattedTimestamp)


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

def grabCC2():
	first = urllib.urlopen("http://homematic-cc2/config/xmlapi/devicelist.cgi").read()
	second = urllib.urlopen("http://homematic-cc2/config/xmlapi/statelist.cgi").read()

	devices = xml.dom.minidom.parseString(first)
	states = xml.dom.minidom.parseString(second)

#	print(devices)
#	print(states)	
	for device in states.childNodes[0].childNodes:
		deviceName = device.getAttribute("name")
		deviceType = getDeviceType(devices, deviceName)
		values = {}

		for channel in device.childNodes:
			for datapoint in channel.childNodes:
				type = datapoint.getAttribute("type")
				value = datapoint.getAttribute("value")
				value = getDomainSensorValue(deviceType, type, value)

				values[type] = value

		recordSensorMeasurement(deviceName,deviceType, values)

def keepGrabbingCC2():
	while(True):
		grabCC2()
		print("pulled data from CC2")
		time.sleep(5.0)

def startRESTService():
    app.run(port='5002', host= '0.0.0.0')
 
if __name__ == "__main__":
    thread = threading.Thread(target=startRESTService)
    thread.daemon = True
    thread.start()
    print("started REST service")

    thread2 = threading.Thread(target=keepGrabbingCC2)
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

