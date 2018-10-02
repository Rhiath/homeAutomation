#include <Adafruit_Sensor.h>

#include <DHT_U.h>
#include <DHT.h>

#include <SPI.h>

#include <RF24_config.h>
#include <RF24.h>
#include <nRF24L01.h>
#include <printf.h>
#define SIGRD 5
#include <avr/boot.h>
#include "LowPower.h"


RF24 radio (9, 10);
byte buffer[128];
byte serial[10];
DHT dht(2, DHT22);

uint64_t addresses[] = {0x314e6f6465};

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(9600);
  Serial.println("booting");


  Serial.print("Serial Number : 0x");
  for (uint8_t i = 14; i < 24; i += 1) {
    // Serial.print(" 0x");
    Serial.print(boot_signature_byte_get(i), HEX);
    serial[i - 14] = boot_signature_byte_get(i);
    Serial.print(".");
  }
  Serial.println();

  Serial.println("Power up RF24");
  delay(100);
  Serial.println(" +--> radio.begin()"); delay(100);
  delay(100);  radio.begin();
  Serial.println(" +--> setting power level"); delay(100);
  radio.setPALevel(RF24_PA_MAX);
  Serial.println(" +--> opening writing pipe"); delay(100);
  radio.openWritingPipe(addresses[0]);
    Serial.println(" +--> opening reading pipe"); delay(100);
  // radio.openReadingPipe(1, addresses[0]);
  Serial.println("completed RF24 power up"); delay(100);
  delay(100);
}

unsigned int lastEmit = 0;

void loop() {
  delay(2000);

  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  emitMessage();
  digitalWrite(LED_BUILTIN, LOW);

  //  for (int x = 0; x < 1; x++) {
  //    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  //  }
}

void emitMessage() {

  float hum = dht.readHumidity();
  float temp = dht.readTemperature();
  Serial.print(temp); Serial.println(" C");
  Serial.print(hum); Serial.println("% RH");

  emit(hum, temp);
}

void emit(float humidity, float temperature) {
  Serial.println();
  String message = String("");
  for (uint8_t i = 0; i < sizeof(serial); i += 1) {
    message = message + String(serial[i], 16);
  }
  message = message + ":";
  char temp[6];
  dtostrf(humidity, 5, 1, temp);
  message = message + temp;
  message = message + ":";
  dtostrf(temperature, 5, 1, temp);
  message = message + temp;

  message.getBytes(buffer, sizeof(buffer));

  Serial.println("sending: " + message + " (" + message.length() + " bytes)");
  radio.write(&buffer, message.length());
  Serial.println("completed send");
}


