from collections import OrderedDict

class Sensor:
	def __init__(self, status):
		self.status = status

	def toHTML(self):
		return self.status

class MultiSensor(Sensor):
	def __init__(self, values):
		t = []
		for sensor in values:
			text = sensor.toHTML()
			t.append(text)
		t = filter(None, t)
		aggregatedSensors = list(OrderedDict.fromkeys(t))
		Sensor.__init__(self, ", ".join(aggregatedSensors))


