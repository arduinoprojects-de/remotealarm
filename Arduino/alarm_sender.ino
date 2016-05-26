
/*
* Getting Started example sketch for nRF24L01+ radios
* This is a very basic example of how to send data from one node to another
* Updated: Dec 2014 by TMRh20
*/
#include <JeeLib.h>
#include <SPI.h>
#include <printf.h>
#include "RF24.h"


ISR(WDT_vect) { Sleepy::watchdogEvent(); } // Setup the watchdog

/****************** User Config ***************************/
/***      Set this radio as radio number 0 or 1         ***/
bool radioNumber = 0;

int pir = 8;
int pirStatus=0;
int stopper = 4;

int led=9;

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 7 & 8 */
RF24 radio(6,7);
/**********************************************************/

byte addresses[][6] = {"1Node","2Node"};

int stopStatus = 0;
int sendTimer = 0;

int stopButtonPressed = 0;

void setup() {
  
  //Serial.begin(115200);
  //Serial.println(F("sender"));
  //Serial.println(F("*** PRESS 'T' to begin transmitting to the other node"));

  //printf_begin();

  pinMode(pir, INPUT);
  pinMode(led, OUTPUT);
  pinMode(stopper, INPUT);

  // thsi is only for prototype
  digitalWrite(led, HIGH);
  delay(300);
  digitalWrite(led, LOW);

  
  radio.begin();

  // Set the PA Level low to prevent power supply related issues since this is a
 // getting_started sketch, and the likelihood of close proximity of the devices. RF24_PA_MAX is default.
  //radio.setPALevel(RF24_PA_MAX);

  radio.setDataRate(RF24_250KBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(102);
  radio.enableDynamicPayloads();
  
  // Open a writing and reading pipe on each radio, with opposite addresses
  if(radioNumber){
    radio.openWritingPipe(addresses[1]);
    radio.openReadingPipe(1,addresses[0]);
  }else{
    radio.openWritingPipe(addresses[0]);
    radio.openReadingPipe(1,addresses[1]);
  }
  
  // Start the radio listening for data
  //radio.startListening();
  radio.powerDown();

  //radio.printDetails();
}

void loop() {
  stopStatus = digitalRead(stopper);

  //Serial.print("sendtimer: ");
  //Serial.println(sendTimer);
 

  if (stopStatus == HIGH || stopButtonPressed > 0) { // check if alarm
    //Serial.println("pushed stop timer - sleep next 15 minutes");
    //delay(10);

    // stop alarm for 30 minutes
    if (stopButtonPressed >= 3) {
      Sleepy::loseSomeTime(30000); // 1000*60*15
      stopButtonPressed = 0;
      sendTimer = 0;
    } else {
      stopButtonPressed++;
    }
  }

  //Serial.print("time: ");
  //Serial.println((millis()/1000));

  pirStatus = digitalRead(pir);

  //Serial.print("PIR STATUS: ");
  //Serial.println(pirStatus);
  //delay(50);

  if (sendTimer >= 10 && (stopButtonPressed == 0 || stopButtonPressed > 3)) {
      //Serial.println("alarm send 10 times - stop for next 15 minutes to save energy");
      //delay(10);
      Sleepy::loseSomeTime(30000); // 1000*60*15
      sendTimer = 0;
    }
    
  
  if (pirStatus == HIGH || sendTimer > 0)  {

    digitalWrite(led, HIGH);
    
    // radio power up
    radio.powerUp();

    radio.stopListening();                                    // First, stop listening so we can talk.
    
    
    //Serial.println(F("Now sending"));

    unsigned long start_time = micros();

    
    if (stopButtonPressed > 0) {
      char message2[] = "car01-2";
      // Take the time, and send it.  This will block until complete
      if (!radio.write( &message2, sizeof(message2) )) {
        //Serial.println(F("failed 2"));
      }
      
    } else {
      char message[] = "car01";
      // Take the time, and send it.  This will block until complete
      if (!radio.write( &message, sizeof(message) )) {
        //Serial.println(F("failed ^1"));
      }

      sendTimer++;
    }
    
    radio.startListening();                      // Now, continue listening
    
    unsigned long started_waiting_at = micros();               // Set up a timeout period, get the current microseconds
    boolean timeout = false;                                   // Set up a variable to indicate if a response was received or not
    
    while ( ! radio.available() ){                             // While nothing is received
      if (micros() - started_waiting_at > 200000 ){            // If waited longer than 200ms, indicate timeout and exit while loop
          timeout = true;
          break;
      }      
    }
        
    if ( timeout ){                                             // Describe the results
       // Serial.println(F("Failed, response timed out."));
    }else{
       unsigned long len = radio.getDynamicPayloadSize();
       //Serial.println(len);
        char messageDebug;        // Grab the response, compare, and send to debugging spew
        radio.read( &messageDebug, sizeof(len)  );
        unsigned long end_time = micros();

        
        // Spew it
        //Serial.print(F("Sent "));
        //Serial.print(start_time);
        //Serial.print(F(", Got response "));
        //Serial.print(messageDebug);
        //Serial.print(F(", Round-trip delay "));
        //Serial.print(end_time-start_time);
        //Serial.println(F(" microseconds"));
        
    }


    digitalWrite(led, LOW);

    // radio power down
    radio.powerDown();

    Sleepy::loseSomeTime(1000);
  } else {
    // no PIR signal detected, sleep 1 second
    Sleepy::loseSomeTime(1000);
  }

} // Loop
