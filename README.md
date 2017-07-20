 # Setup
 This is the Linux/MQTT-server/RaspberryPi setup part of the smart-blind project. Make sur you also have setup the ESP8266 part.
 
* Clone the project on a Unix platform.
* Install the following Python libraries: paho-mqtt, crontab: `pip install paho-mqtt crontab`.
* Create a cron job in you user crontab: `crontab -e` (also see __crontab__ file for example):

```shell
# Will trigger the opening every week day at 7:45
45 7 * * 1-5 ~/smart-blinds/signal.sh > /dev/null 2>&1
```

* In __alarm-blinds.py__ change the MQTT broker's IP address to a free address that match your network (the same as the ESP's one).
* Launch the __alarm-blinds.py__ deamon in the background: `python alarm-blinds.py &`.
* That's it !

## Requirements:
The system time shall be up to date.
The system must be connected to the same network as the ESP8266.