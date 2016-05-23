# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from __future__ import print_function
import time
from datetime import datetime
#import urllib2
import requests
from RF24 import *

radio = RF24(RPI_BPLUS_GPIO_J8_22, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

#pipes = [[0x65, 0x64, 0x6F, 0x4E, 0x32], [0x65, 0x64, 0x6F, 0x4E, 0x31]]
pipes = ["1Node", "2Node"]


print('pyRF24/examples/pingpair_dyn/')
radio.begin()

radio.setDataRate(RF24_250KBPS)
radio.setPALevel(RF24_PA_MIN)
radio.setChannel(102)
radio.enableDynamicPayloads()

radio.setRetries(5, 15)
radio.printDetails()

radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1, pipes[0])

radio.startListening()

car = 'car01'
carStop = 'car01-2'

carAlarm = 0
carAlarmTimer = 0
carAlarmSend = 0
carAlarmStoppedAt = 0
stopAlarmCounter = 0

carAlarmStopTimerMinutes = 1 #10
carAlarmStopTimer = carAlarmStopTimerMinutes * 60

cellar = 'cellar01'
cellarStop = 'cellar01-2'

def sendThingSpeak(value):
    while True:
        print("request thingspeak with {}" . format(value))
        r = requests.get("https://api.thingspeak.com/update.json?api_key=EII2PMU2M8MN7YR9&field1={}" . format(value))
        
        if r.text != '0':
            break
        elif r.text == '0':
            time.sleep(3)
    
    
# create car alarm
def createCarAlarm():
    global carAlarm, carAlarmTimer, carAlarmStoppedAt, carAlarmStopTimer
    
    if carAlarm == 0:
        createNewAlarm = 1
        
        #check time diff betwenn last alarm and now (dont send a new alarm when motion in next 10 minutes
        if carAlarmStoppedAt != 0:
            checkedTime = datetime.now() - carAlarmStoppedAt
            print("checkedTime {}".format(checkedTime.seconds))
            if checkedTime.seconds <= carAlarmStopTimer:
                createNewAlarm = 0
        
        if createNewAlarm == 1:
            carAlarm = 1
            carAlarmTimer = datetime.now()
            stopAlarmCounter = 0
            print("car alarm started at {}".format(carAlarmTimer))
            
            sendThingSpeak(1)
            
        else:
            print("alarm aready sended (create no new alarm for {}) at {}" . format(carAlarmStoppedAt, datetime.now()))
    #else:
    #    print("car alarm already running")
    
    
def stopCarAlarm(stopType):    
    global carAlarm, carAlarmTimer, carAlarmStoppedAt, stopAlarmCounter
    
    if stopType == 1 and stopAlarmCounter == 0:
        sendThingSpeak(0)
        stopAlarmCounter += 1
    
    print("stop car alarm at {}" . format(datetime.now()))
    
    carAlarm = 0
    carAlarmTimer = 0
    checkTimer = 0
    
    
    
    
    
def checkCarAlarm():
    global carAlarm, carAlarmTimer
    
    if carAlarm == 1:
        #print("check Car Alarm {}" . format(carAlarmTimer))
        checkTimer = datetime.now() - carAlarmTimer

        #print("checkTimer: {}" . format(checkTimer.seconds))

        if checkTimer.seconds > 10:
            sendAlarm('carAlarm', 'Unbefugte Bewegung in CAR01')
        elif checkTimer.seconds < 10:
            pass
            #print("we have time :)")
    
    
def sendAlarm(alarmType, message):
    global carAlarmSend, carAlarmStoppedAt
    
    if carAlarmSend == 0:
        print("sendAlarm type={} message={}" . format(alarmType, message))
        
        carAlarmStoppedAt = datetime.now()
        stopCarAlarm(0)
    else:
        print("car alarm already send")
    
    

while True:
    ackPL = [1]

    checkCarAlarm()

    while not radio.available():
        time.sleep(10/100)
        checkCarAlarm()

    len = radio.getDynamicPayloadSize()
    receive_payload = radio.read(len)

    response = receive_payload.decode('utf-8')
    
    string = ""
    for n in response:
        if (n != '\x00'):
            string += n.encode('ascii')
       
    
    responseType = ''
    if string == car:
        responseType = 'car'
        createCarAlarm()
    elif string == carStop:
        stopCarAlarm(1)
    elif string == cellar:
        responseType = 'cellar'
        print("start cellar alarm")
    elif string == cellarStop:
        pirnt("stop cellar alarm")
    else:
        responseType = 'unknown'
    
    print('Got payload size={} value="{}" in type="{}"'.format(len, response, responseType))
    
    radio.stopListening()
    radio.write(receive_payload)
    print('Sent response.')
    
    radio.startListening()
