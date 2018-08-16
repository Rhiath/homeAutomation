#include <SPI.h>

#include <RF24_config.h>
#include <RF24.h>
#include <nRF24L01.h>
#include <printf.h>
#define SIGRD 5
#include <avr/boot.h>

RF24 radio (9,10);
byte buffer[128];
byte serial[10];

uint64_t addresses[]= {0x314e6f6465};
int nodeID;

void setup(){
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
  unsigned int now = millis();
  if( now - lastEmit > 5000){
    emitMessage();
    lastEmit = now;
  }
  if ( lastEmit > millis()) { 
   emitMessage();
    lastEmit = now;
  }
  //Serial.println(String("now: ")+now+" lastEmit: "+lastEmit);
  
  receiveMessages();
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
 emit("T", 100);
 emit("H", 23);
    radio.startListening();

}

void emit(String type, int value) {
 Serial.println();
  String message = String("");
   for (uint8_t i = 0; i < sizeof(serial); i += 1) {
    message = message + String(serial[i],16);
  }
  message = message + ":";
  message = message + type;
  message = message + value;
  
  message.getBytes(buffer,sizeof(buffer));

  Serial.println("sending: "+message+" ("+message.length()+" bytes)");
  radio.write(&buffer,message.length());
  
}


