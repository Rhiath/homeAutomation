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


RF24 radio (9,10);
byte buffer[128];
byte serial[10];
DHT dht(2, DHT22);

uint64_t addresses[]= {0x314e6f6465};
int nodeID;
#define DHT_GND 3

void setup(){
  pinMode(DHT_GND, OUTPUT); 
  digitalWrite(DHT_GND, LOW);

   
  radio.begin();
  radio.setPALevel(RF24_PA_MAX); 
  radio.openWritingPipe(addresses[0]);
  radio.openReadingPipe(1,addresses[0]);
  Serial.begin(9600);
  randomSeed(analogRead(0));
  nodeID = random(3000);


 /*   Serial.print("Signature : ");
    for (uint8_t i = 0; i < 5; i += 2) {
        Serial.print(" 0x");
        Serial.print(boot_signature_byte_get(i), HEX);
    }
    Serial.println();
*/
    Serial.print("Serial Number : 0x"); 
    for (uint8_t i = 14; i < 24; i += 1) {
       // Serial.print(" 0x");
        Serial.print(boot_signature_byte_get(i), HEX);
        serial[i-14] = boot_signature_byte_get(i);
    }
// Serial.println();
  
}

unsigned int lastEmit = 0;

void loop() {
  delay(2000);
  emitMessage();
  for (int x = 0; x < 8; x++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  }
}

void receiveMessages(){
    unsigned long started_waiting_at = millis();               // Set up a timeout period, get the current microseconds
    boolean timeout = false;                                   // Set up a variable to indicate if a response was received or not
int timeoutValue = 200;
    
    while ( ! radio.available() ){                             // While nothing is received
      if (millis() - started_waiting_at > (timeoutValue) ){            // If waited longer than 200ms, indicate timeout and exit while loop
          timeout = true;
          break;
      }      
    }
        
    if ( timeout ){                                             // Describe the results
       Serial.print(".");
    }else{
      unsigned long start_time = millis();    
       radio.read( &buffer, sizeof(buffer) );
        unsigned long end_time = millis();

        String message = String((char*) buffer);
        Serial.println(String("received (@nodeID:")+nodeID+"]: "+message+" ("+message.length()+" bytes)");

        // Spew it
    /*    Serial.print(F("started reception at "));
        Serial.print(start_time);
        Serial.println(F(" millis"));
     
        Serial.print(F("ended reception at "));
        Serial.print(end_time-start_time);
        Serial.println(F(" millis")); */
}

}

void emitMessage() {
  radio.stopListening();

 float hum = dht.readHumidity();
 float temp = dht.readTemperature();
Serial.print(temp);Serial.println(" C");
Serial.print(hum);Serial.println("% RH");
 emit(hum,temp);
// emit("T", 100);
// emit("H", 23);
    radio.startListening();

}

void emit(float humidity, float temperature) {
 Serial.println();
  String message = String("");
   for (uint8_t i = 0; i < sizeof(serial); i += 1) {
    message = message + String(serial[i],16);
  }
  message = message + ":";
  char temp[6];
  dtostrf(humidity, 5,1,temp);
  message = message + temp;
  message = message + ":";
  dtostrf(temperature, 5,1,temp);
  message = message + temp;
  
  message.getBytes(buffer,sizeof(buffer));

  Serial.println("sending: "+message+" ("+message.length()+" bytes)");
  radio.write(&buffer,message.length());
  
}


