# remotealarm

Arduino / Raspberry Pi remote alarm system

* sender (Arduino - lowpower breadboard Atmega328) - code coming soon
* receiver (Raspberry Pi - base station with internet connection)

* visualize data with thingspeak.com

# librarys

* NRF24L01 Library (runs on arduino with C and on Raspberry Pi with Python) - https://github.com/TMRh20/RF24

# versions

    1.0.0 - base version
    1.1.0 - add ThingSpeak Api to show alarms in web
    1.2.0 - add InnoSend sms gateway for alarm messages