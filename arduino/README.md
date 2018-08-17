# Goal
Measure temperture and humidity in regular intervals and send them to the central processing hub for processing

# current state
Every 5 seconds, the code emits two sensor values: 100°C and 23% relative humidity.

Example: "00112233445566778899:T034" for 34°C from sensor node "00112233445566778899"

# planned features
Read the current temperature and humidity from a DHT22 sensor
