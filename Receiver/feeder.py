from xml.dom.minidom import parse
import xml.dom.minidom
import json
import jsonpickle
import building
import time
import urllib2
import datetime

def getDeviceType(devices, deviceName):
        for device in devices.childNodes[0].childNodes :
#               print(device.getAttribute("name")+" vs. "+deviceName)
                if (device.getAttribute("name") == deviceName ):
                        return device.getAttribute("device_type")
        return "unknown";


def buildSensorMap(theBuilding):
	retValue = {}

	for floor in theBuilding.floors :
		for room in floor.rooms :
			for window in room.windows :
				for sensor in window.sensors :
					retValue[sensor.name] = sensor
			for door in room.doors :
				for sensor in door.sensors :
					retValue[sensor.name] = sensor
			for sensor in room.sensors :
					retValue[sensor.name] = sensor

		if ( not floor.hallway == None ):
			for window in floor.hallway.windows :
				for sensor in window.sensors :
					retValue[sensor.name] = sensor
			for door in floor.hallway.doors :
				for sensor in door.sensors :
					retValue[sensor.name] = sensor
			for sensor in floor.hallway.sensors :
					retValue[sensor.name] = sensor


	return retValue

def getDomainSensorValue(deviceType, sensorType, value):
        if (deviceType == "HM-Sec-SC-2" and sensorType == "STATE"):
                if ( value == "true"): value = "OPEN"
                if ( value == "false"): value = "CLOSED"

        if (deviceType == "HM-Sec-RHS" and sensorType == "STATE"):
                if ( value == "0"): value = "LOCK"
                if ( value == "1"): value = "TILT"
                if ( value == "2"): value = "UNLOCK"


        return value;


def feedFromCC2(sensors, hostAndPort):
        try:
                first = urllib2.urlopen("http://"+hostAndPort+"/config/xmlapi/devicelist.cgi", timeout=5).read()
                second = urllib2.urlopen("http://"+hostAndPort+"/config/xmlapi/statelist.cgi", timeout=5).read()
        except Exception as e:
                print(e)
                print("failed to pull data from homematic CC2")
                return

	try:
	        devices = xml.dom.minidom.parseString(first)
        	states = xml.dom.minidom.parseString(second)
        except Exception as e:
                print(e)
                print("failed to pull data from homematic CC2")
                return

#       print(devices)
#       print(states)
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

		if ( deviceName in sensors ):
			sensors[deviceName].set(deviceType, values, now())

def now():
	return makePrettyTimestamp(time.time())

def makePrettyTimestamp(timestamp):
        retValue = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
        return retValue


def keepFeedingFromCC2(building, delayInSecondsBetweenFeeds, hostAndPort):
	sensors = buildSensorMap(building)
	while ( True ) :
		time.sleep(delayInSecondsBetweenFeeds)
		feedFromCC2(sensors, hostAndPort)


if __name__ == "__main__":
	document = xml.dom.minidom.parse("building.xml")
	element = document.childNodes[0]

	building = Building(element)
	


	print(jsonpickle.encode(building, unpicklable=False))
