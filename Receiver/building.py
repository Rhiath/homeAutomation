class Building:
	def __init__(self, floors):
		self.floors = floors

class Floor:
	def __init__(self, name, rooms, hallways):
		self.name = name
		self.rooms = rooms
		self.hallways = hallways

class Room:
	def __init__(self, name, windows, doors, sensors):
		self.name = name
		self.windows = windows
		self.doors = doors

class Window:
	def __init__(self, name, sensors):
		self.name = name
		self.sensors = sensors

class Door:
	def __init__(self, name, sensors):
		self.name = name
		self.sensors = sensors

class Sensor:
	type = "unknown"
	values = []

	def __init__(self, name):
		self.name = name

	def setType(self, type):
		self.type = type

	def setValues(self, values):
		self.values = values

	def setLastMeasurement(self, timestamp):
		self.lastMeasurement = timestamp




