# Goal
Measure temperature and humidity in regular intervals and send them to the central processing hub for processing

# current state
Every 5 seconds, the code emits the temperature and the humidity as measured by the DHT22 sensor that is connected to the arduino.

Example: "00112233445566778899: 52.7: 25.4" for 52.7% RH and 25.4°C from sensor node "00112233445566778899"

# TODO
Remove reading of data and go into a "low power mode" when no data is to be transmitted (increases battery life)
