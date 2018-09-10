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
import rf24Feeder

 
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

def startRESTService():
    app.run(port='5002', host= '0.0.0.0')
 
if __name__ == "__main__":
    print("starting CC2 grabber")
    thread2 = threading.Thread(target=feeder.keepFeedingFromCC2, args=(theBuilding, 5.0, "homematic-cc2",))
    thread2.daemon = True
    thread2.start()
    print("started CC2 grabber")

    print("starting RF24 grabber")
    thread3 = threading.Thread(target=rf24Feeder.keepFeedingFromRF24, args=(theBuilding,))
    thread3.daemon = True
    thread3.start()
    print("started RF24 grabber")

    print("starting REST service")
    thread = threading.Thread(target=startRESTService)
    thread.daemon = True
    thread.start()
    print("started REST service")

    thread.join()
    thread2.join()
    thread3.join()

