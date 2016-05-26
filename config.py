useThingSpeak = 1
useInnoSend = 1

base = dict(
    thingspeak = dict(
        apikey = 'YOURTHINGSPEAKAPIKEY'
    )
)

alarms = dict(
    car = dict(
        start = 'car01',
        stop  = 'car01-2',
        stopMinutes = 1 #10
    ),
    cellar = dict(
        start = 'cellar01',
        stop  = 'cellar01-2',
        stopMinutes = 1 #10
    )
)
