#!/usr/bin/env python
#from __future__ import print_function
import time
import sys
from RF24 import *
import RPi.GPIO as GPIO
 
button_pin  = 16        # GPIO number
codeOn      = "Turn LED on"
codeOff     = "Turn LED off"
 
# RPi Alternate, with SPIDEV - Note: Edit RF24/arch/BBB/spi.cpp and  set 'this->device = "/dev/spidev0.0";;' or as listed in /dev
radio = RF24(22, 0);
 
pipes = [0x314e6f6465]
payload_size = 32
millis = lambda: int(round(time.time() * 1000))
 
radio.begin()
 
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1,pipes[0])
 
def sendCode(code):
    # The payload will always be the same, what will change is how much of it we send.
 
    # First, stop listening so we can talk.
    radio.stopListening()
 
    # Take the time, and send it.  This will block until complete
    radio.write(code[:payload_size])
 
    # Now, continue listening
    radio.startListening()
 
 
if __name__ == "__main__":
 
    led_status = False
 
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
 
    while True:
	radio.startListening()            
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
		print(receive_payload)

    	# First, stop listening so we can talk.
    	radio.stopListening()
 
    	# Take the time, and send it.  This will block until complete
    	#radio.write("Hallo Welt"[:payload_size])
 
        #time.sleep(0.1)
#	sys.stdout.write(".")
	#sys.stdout.flush()
