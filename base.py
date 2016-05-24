# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from __future__ import print_function
import time
from datetime import datetime
import requests
from RF24 import *
import config

radio = RF24(RPI_BPLUS_GPIO_J8_22, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

#pipes = [[0x65, 0x64, 0x6F, 0x4E, 0x32], [0x65, 0x64, 0x6F, 0x4E, 0x31]]
pipes = ["1Node", "2Node"]

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

alarm = dict()
alarmTimer = dict()
alarmSend = dict()
alarmStoppedAt = dict()
alarmStopTimer = dict()
alarmStopCounter = dict()
checkTimer = dict()
for alarmType in config.alarms:
    alarm[alarmType] = 0
    alarmTimer[alarmType] = 0
    alarmSend[alarmType] = 0
    alarmStoppedAt[alarmType] = 0
    alarmStopCounter[alarmType] = 0
    checkTimer[alarmType] = 0
    
    alarmStopTimer[alarmType] = config.alarms[alarmType]['stopMinutes'] * 60


def sendThingSpeak(value):
    while True:
        print("request thingspeak with {}" . format(value))
        r = requests.get("https://api.thingspeak.com/update.json?api_key={}&field1={}" . format(config.base['thingspeak']['apikey'], value))
        
        if r.text != '0':
            break
        elif r.text == '0':
            time.sleep(3)
    
    
# create car alarm
def createAlarm(type):
    global alarmTimer, alarmStoppedAt, alarmStopTimer
    global alarm
    
    if alarm[type] == 0:
        createNewAlarm = 1
        
        #check time diff betwenn last alarm and now (dont send a new alarm when motion in next 10 minutes
        if alarmStoppedAt[type] != 0:
            checkedTime = datetime.now() - alarmStoppedAt[type]
            print("checkedTime {}".format(checkedTime.seconds))
            if checkedTime.seconds <= alarmStopTimer[type]:
                createNewAlarm = 0
        
        if createNewAlarm == 1:
            alarm[type] = 1
            alarmTimer[type] = datetime.now()
            alarmStopCounter[type] = 0
            print("car alarm started at {}".format(alarmTimer[type]))
            
            if config.useThingSpeak == 1:
                sendThingSpeak(1)
            
        else:
            print("alarm aready sended (create no new alarm for {}) at {}" . format(alarmStoppedAt[type], datetime.now()))
    #else:
    #    print("car alarm already running")
    
    
def stopAlarm(type, stopType):    
    global alarmTimer, alarmStoppedAt, alarmStopCounter, alarm, checkTimer
    
    if stopType == 1 and alarmStopCounter[type] == 0:
        if config.useThingSpeak == 1:
            sendThingSpeak(0)
        alarmStopCounter[type] += 1
    
    print("stop car alarm at {}" . format(datetime.now()))
    
    alarm[type] = 0
    alarmTimer[type] = 0
    checkTimer[type] = 0
    
    
    
    
    
def checkAlarm(type):
    global alarmTimer, alarm, checkTimer
    
    if alarm[type] == 1:
        #print("check Car Alarm {}" . format(alarmTimer[type]))
        checkTimer[type] = datetime.now() - alarmTimer[type]

        #print("checkTimer: {}" . format(checkTimer.seconds))

        if checkTimer[type].seconds > 10:
            sendAlarm(type, 'carAlarm', 'Unbefugte Bewegung in CAR01')
        elif checkTimer[type].seconds < 10:
            pass
            #print("we have time :)")
    
    
def sendAlarm(type, alarmType, message):
    global alarmSend, alarmStoppedAt
    
    if alarmSend[type] == 0:
        print("sendAlarm type={} message={}" . format(alarmType, message))
        
        alarmStoppedAt[type] = datetime.now()
        stopAlarm(type, 0)
    else:
        print("car alarm already send")
    
    

while True:
    ackPL = [1]

    checkAlarm('car')

    while not radio.available():
        time.sleep(10/100)
        checkAlarm('car')

    len = radio.getDynamicPayloadSize()
    receive_payload = radio.read(len)

    response = receive_payload.decode('utf-8')
    
    string = ""
    for n in response:
        if (n != '\x00'):
            string += n.encode('ascii')
       
    for alarmType in config.alarms:
        if string == config.alarms[alarmType]['start']:
            createAlarm(alarmType)
        elif string == config.alarms[alarmType]['stop']:
            stopAlarm(alarmType, 1)
        
    print('Got payload size={} value="{}"'.format(len, string))

    radio.stopListening()
    radio.write(receive_payload)
    print('Sent response.')

    radio.startListening()
