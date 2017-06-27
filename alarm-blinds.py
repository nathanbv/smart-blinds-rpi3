import os
import paho.mqtt.client as mqtt
import signal
import threading
from crontab import CronTab

# Local MQTT settings
mqttBroker  = "192.168.178.21"          # Broker
mqttPort    = 1883                      # Port
mqttTimeOut = 120                       # Session timeout
mqttUser    = "smart-blinds"            # User
mqttPass    = "wakemeupbeforeyougogo"   # Password
mqttAlarmOut   = "trigger-alarm"        # Topic to write
mqttAlarmIn    = "trigger-alarm_ACK"    # Topic to read
mqttTimeSetOut = "set-alarm-time_ACK";  # Topic to write
mqttTimeSetIn  = "set-alarm-time";      # Topic to read

class MQTTAlarm():
    def __init__(self):
        # Global states
        self.mqttClient = None
        self.timerPub = None

    def on_connect(self, mqttClient, userdata, flags, rc):
        print "Connected:", str(rc)
        mqttClient.subscribe(mqttAlarmIn)
        mqttClient.subscribe(mqttTimeSetIn)

    def publish_loop(self):
        print "Sending [trigger-alarm]..."
        self.mqttClient.publish(mqttAlarmOut, "1")

    def on_signal(self, signum, frame):
        print "Signal handler called with signal [%r]" % (signum)
        # Re-publish waiting for ACK every 5s
        self.timerPub = threading.Timer(5.0, self.publish_loop)
        self.timerPub.start()

    def change_timetable(self, newTime):
        h = newTime[1:3]
        m = newTime[3:5]
        print "Updating cron table with %dh %dm" % (h, m)
        try:
            cron = CronTab(user=True) # Get the crontab from current user
            match = cron.find_command('signal.sh')
            for job in match:
                if (job.is_enabled() == True) and (job.is_valid() == True):
                    job.minute.on(m) # Set to m * * * *
                    job.hour.on(h)   # Set to * h * * *
                    print job
                else:
                    print "A wrong job was found"
            cron.write_to_user(user=True) # Write back the table to the system
        except ValueError:
            print "Wrong value hours must be [0:23] and minutes must be [0:59]"
        print "Cron table updated, sending ACK"
        self.mqttClient.publish(mqttTimeSetOut, "2") # Send ACK

    def on_message(self, mqttClient, userdata, msg):
        if msg.payload[0] == 's':
            print "Received [set-alarm-time] [%r]" % (msg.payload)
            self.change_timetable(msg.payload)

        elif msg.payload[0] == '2':
            print "Received [trigger-alarm_ACK] [%r]" % (msg.payload)
            self.timerPub.cancel()

    def main(self):
        # Initialize client's MQTT connection
        self.mqttClient = mqtt.Client()
        self.mqttClient.username_pw_set(mqttUser, mqttPass)

        # Assign callbacks for MQTT
        self.mqttClient.on_connect    = self.on_connect
        self.mqttClient.on_message    = self.on_message
        # Assign callback for kernel signal
        signal.signal(signal.SIGUSR1, self.on_signal)

        # Connect, wait for callbacks and monitor topic forever
        self.mqttClient.connect(mqttBroker, mqttPort, mqttTimeOut)
        self.mqttClient.loop_forever(retry_first_connection=True)

if "__main__" == __name__:
    alarm = MQTTAlarm()
    alarm.main()
    quit() # Never happens
