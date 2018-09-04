import time
import datetime
import sys
from flask import Flask, request, make_response, Response
from flask_restful import Api, Resource
from json import dumps
import urllib2
from xml.dom.minidom import parse
import xml.dom.minidom
import sensors
import building
import jsonpickle
import feeder

class Renderer(Resource):

    def __init__(self, theBuilding):
	self.theBuilding = theBuilding

    @staticmethod
    def getChildren(element, name):
	retValue = []
	for child in element.childNodes:
		if ( child.nodeName == name ):
			retValue.append(child)
	return retValue

    def renderSensors(self, element):
	retValue = "";
	values = []
	for sensor in element.sensors:
		name = sensor.name
		value = self.renderSensorValue(sensor)
		sens = sensors.Sensor(value)
		values.append(sens)
		values.append(sensors.Sensor(self.renderBatteryStatus(sensor)))
		values.append(sensors.Sensor(self.renderStickyDisconnect(sensor)))
	multi = sensors.MultiSensor(values)
	return multi.toHTML()

    def renderSensorValue(self, element):
	name = element.name
	retValue = "unknown"

	if ( hasattr(element, "type") and hasattr(element, "values") and hasattr(element, "lastMeasurement")):
		sensorType = element.type
		retValue = element.values["STATE"]

	if ( retValue == "OPEN" or retValue == "UNLOCK" ):
		retValue = "<font color=\"red\">"+retValue+"</font>"

	if ( retValue == "TILT" ):
		retValue = "<font color=\"GoldenRod\">"+retValue+"</font>"

	if ( retValue == "CLOSED" or retValue == "LOCK" ):
		retValue = "<font color=\"green\">"+retValue+"</font>"

	return retValue;

    def renderBatteryStatus(self, element):
	name = element.name
	retValue = ""

	if ( hasattr(element, "type") and hasattr(element, "values") and hasattr(element, "lastMeasurement")):
		sensorType = element.type
		retValue = element.values["LOWBAT"]

	if ( retValue == "true" ):
		retValue = "<font color=\"red\">LOW BATTERY</font>"
	if ( retValue == "false" ):
		retValue = ""

	return retValue;

    def renderStickyDisconnect(self, element):
	name = element.name
	retValue = ""

	if ( hasattr(element, "type") and hasattr(element, "values") and hasattr(element, "lastMeasurement")):
		sensorType = element.type
		retValue = element.values["STICKY_UNREACH"]

	if ( retValue == "true" ):
		retValue = "<font color=\"GoldenRod\">UNREACHABLE</font>"
	if ( retValue == "false" ):
		retValue = ""

	return retValue;


    def renderRoom(self, room):
	retValue = "";
	retValue = retValue + "<h2>" + room.name + "</h2>"
	retValue = retValue + self.renderSensors(room)
	for door in room.doors:
		retValue = retValue + self.renderDoor(door)
	for window in room.windows:
		retValue = retValue + self.renderWindow(window)
	return retValue

    def renderDoor(self, element):
	return "<b>"+element.name+" [" + self.renderSensors(element)+"]</b><br />"

    def renderWindow(self, element):
	return "<b>"+element.name+" [" + self.renderSensors(element)+"]</b><br />"

    def get(self):
        retValue = "<html><head><meta http-equiv=\"refresh\" content=\"5\"></head><body>"

	# building = xml.dom.minidom.parse("building.xml")
	# retValue = retValue + "<b>last connection to CC2: "+makePrettyTimestamp(lastConnectionToCC2)+"</b>"
	for floor in self.theBuilding.floors:
		retValue = retValue + "<h1>" + floor.name + "</h1>"
		if ( floor.hallway != None ):
			for door in floor.hallway.doors:
				retValue = retValue + self.renderDoor(door)
			for window in floor.hallway.windows:
				retValue = retValue + self.renderWindow(door)
		for room in floor.rooms:
			retValue = retValue + self.renderRoom(room)

	retValue = retValue + "</body></html>"
	return make_response(retValue, 200)

def makePrettyTimestamp(timestamp):
	retValue = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
	return retValue

