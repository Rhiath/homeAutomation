# homeAutomation
## Goal
I was in the need of measuring the temperature and humidity at several location (both inside and outside). As commercial solution were too expensive, a DIY solution was initiated.

## (Target) Solution
Have a battery powered Arduino Nano board location whereever I need it and have it measure and transmit the relevant data to a central processing hub (a raspberry pi). Transmission was decided to be performed using RF24 boards, so I don't have to put wires to all locations I need a sensor.

### Communication Protocol (RF24)
As the RF24 chips support a maximum message length of 32 byte (and I didn't want to be bothered with message fragmentation and re-assembly), I put all the data I need into the 32 bytes. Every message starts with the Arduino ID in hex (read from the bootload of the chip), followed by a colon and then the sensor data. To support multiple sensor values, every type of sensor data is identified by a single character. After the sensor type character, there are sensor type specific characters.

For example:
00112233445566778899:T+034

In the example above, the arduino chip has the ID "00112233445566778899" (10 bytes in hex). The sensor type is "T" (for temperature, measured in °C). The value is +34°C.

