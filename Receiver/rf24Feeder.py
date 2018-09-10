from xml.dom.minidom import parse
import xml.dom.minidom
import json
import jsonpickle
import building
import time
import urllib2
import datetime

from RF24 import *
import RPi.GPIO as GPIO

millis = lambda: int(round(time.time() * 1000))

# RPi Alternate, with SPIDEV - Note: Edit RF24/arch/BBB/spi.cpp and  set 'this->device = "/dev/spi$

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

def handleMessage(message, sensors):
        nodeID = getNodeID(message)
        humidity = getHumidity(message)
        temperature = getTemperature(message)

#       print(nodeID+" --> "+humidity+" RH, "+temperature+" C")
        values = {}
        values["T"] = temperature
        values["H"] = humidity
        print(nodeID +"(DHT22) --> "+ json.dumps(values))

	sensors[nodeID].set("DHT22", values, now())

def now():
        return makePrettyTimestamp(time.time())


def getDeviceType(devices, deviceName):
        for device in devices.childNodes[0].childNodes :
#               print(device.getAttribute("name")+" vs. "+deviceName)
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


def keepFeedingFromRF24(building):
    pipes = [0x314e6f6465]
    payload_size = 32

    radio = RF24(22, 0);

    radio.begin()

    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1,pipes[0])

    sensors = buildSensorMap(building)
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
                handleMessage(receive_payload, sensors)


if __name__ == "__main__":
	document = xml.dom.minidom.parse("building.xml")
	element = document.childNodes[0]

	building = Building(element)
	


	print(jsonpickle.encode(building, unpicklable=False))
