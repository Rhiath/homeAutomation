# homeAutomation
## Goal
I was in the need of measuring the temperature and humidity at several location (both inside and outside). As commercial solution were too expensive, a DIY solution was initiated.

## (Target) Solution
Have a battery powered Arduino Nano board location whereever it is needed and have it measure and transmit the relevant data to a central processing hub (a raspberry pi). Transmission was decided to be performed using nRF24L01+ boards, so it is not necessary to put wires to all locations a sensor node is placed.

### Communication Protocol (RF24)
As the RF24 chips support a maximum message length of 32 byte (and I didn't want to be bothered with message fragmentation and re-assembly), I put all the data I need into the 32 bytes. Every message starts with the Arduino ID in hex (read from the bootload of the chip), followed by a colon separated sensor values. The first sensor value is the humidity (in % relative humidity), the second one is temperature (in °C). Each sensor value is 5 characters long (right aligned; padded with spaces as needed). This results in 31 byte long messages.

Example:
00112233445566778899: 52.7: 25.4

In the example above, the arduino chip has the ID "00112233445566778899" (10 bytes in hex). The temperature is +25.4°C and the humidity is 52.7% RH.

The protocol is unidirectional (from sensor nodes to raspberry pi) without any ACK (i.e. "data received") messages. This makes it similar to UDP communication. All messages by all sensor nodes are posted to the same channel, making it possible to add new sensor nodes without changing the raspberry pi configuration. That is also the reason why there is a sensor node ID in every message: this makes it possible to associate the sensor values with the sensor nodes that emitted them.
