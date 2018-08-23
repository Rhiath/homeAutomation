from xml.dom.minidom import parse
import xml.dom.minidom
import json
import jsonpickle

class Building:
	def __init__(self, element):
		self.floors = []
	        for floor in getChildren(element,"floor"):
        	        self.floors.append(Floor(floor))

class Floor:
	def __init__(self, element):
		self.name = element.getAttribute("name")
		self.rooms = []
	        for room in getChildren(element,"room"):
        	        self.rooms.append(Room(room))

		self.hallway = None
	        for child in getChildren(element,"hallway"):
        	        self.hallway = Hallway(child)

class Room:
	def __init__(self, element):
		self.name = element.getAttribute("name")
		self.windows = []
	        for window in getChildren(element,"window"):
        	        self.windows.append(Window(window))

		self.doors = []
	        for door in getChildren(element,"door"):
        	        self.doors.append(Door(door))

class Hallway:
	def __init__(self, element):
		self.sensors = []
	        for sensor in getChildren(element,"sensor"):
        	        self.sensors.append(Sensor(sensor))
		self.windows = []
	        for window in getChildren(element,"window"):
        	        self.windows.append(Window(window))

		self.doors = []
	        for door in getChildren(element,"door"):
        	        self.doors.append(Door(door))

class Window:
	def __init__(self, element):
		self.name = element.getAttribute("name")
		self.sensors = []
	        for sensor in getChildren(element,"sensor"):
        	        self.sensors.append(Sensor(sensor))

class Door:
	def __init__(self, element):
		self.name = element.getAttribute("name")
		self.sensors = []
	        for sensor in getChildren(element,"sensor"):
        	        self.sensors.append(Sensor(sensor))

class Sensor:
	type = "unknown"
	values = []

	def __init__(self, element):
		self.name = element.getAttribute("name")

	def setType(self, type):
		self.type = type

	def setValues(self, values):
		self.values = values

	def setLastMeasurement(self, timestamp):
		self.lastMeasurement = timestamp



def getChildren(element, name):
    retValue = []
    for child in element.childNodes:
        if ( child.nodeName == name ):
            retValue.append(child)
    return retValue


if __name__ == "__main__":
	document = xml.dom.minidom.parse("building.xml")
	element = document.childNodes[0]

	building = Building(element)

	print(jsonpickle.encode(building, unpicklable=False))
