# meter.py - the MQTT voltmeter: shows total solar PV power on the old dial.
# Copy it to the board as main.py, with pointer.py and your Secrets.py beside it.
# It joins WiFi and the MQTT broker, adds up the PV power from the topics listed
# in Secrets.py, and glides the pointer to watts ÷ 10 (600 on the dial = 6000 W).
# Ctrl-C at the console stops it. Then you can type:
#   dial(450)     glide the pointer to 450 on the dial (0 to 600)
#   duty(50)      jump straight to 50 % duty (any number from 0 to 100)
#   freq(1000)    change the PWM frequency to 1000 Hz
#   run()         start showing PV power again
# History:
#   v9 the topics to show live in Secrets.py
#   v8 pointer code moved to pointer.py, shared with demo.py
#   v7 renamed from pwm-test.py; WiFi and MQTT, shows total PV power
#   v6 calibration for the pulsed drive
#   v5 100 Hz pulsed drive (no smoothing capacitor); shake() removed
#   v4 shake() to test clearing the meter's leftover magnetism
#   v3 glide takes a fixed time along an S-curve, no slow crawl at the end
#   v2 dial() with the calibration table, gliding so the pointer doesn't overshoot
#   v1 first version

import time
import json
import network
from umqtt.simple import MQTTClient

import Secrets        # your WiFi, broker and topics: see SecretsExample.py
from pointer import dial, duty, freq   # duty and freq are for the console

VERSION = 9

# What to show: the number called KEY in each of the MQTT topics listed in
# Secrets.py, added together, then divided by SCALE to give the dial reading.
TOPICS = Secrets.TOPICS
KEY = "PvW"           # PV power in watts
SCALE = 10            # 6000 W = 600 on the dial

UPDATE_S = 10         # move the pointer this often, in seconds
STALE_S = 60          # a topic that's been quiet this long counts as 0
PING_S = 30           # tell the broker we're still here this often
CLIENT_ID = "Voltmeter"

# The latest value from each topic, and when it arrived.
latest = {}
heard_at = {}


def on_message(topic, message):
    # The MQTT library calls this for every message on our topics.
    topic = topic.decode()
    data = json.loads(message.decode())
    if KEY in data:
        latest[topic] = data[KEY]
        heard_at[topic] = time.time()


def total():
    # Add up the latest value from each topic, leaving out any that have gone quiet.
    now = time.time()
    watts = 0
    for topic in TOPICS:
        if topic in latest and now - heard_at[topic] < STALE_S:
            watts = watts + latest[topic]
    return watts


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return
    print("Connecting to WiFi", Secrets.WIFI_NAME)
    wlan.connect(Secrets.WIFI_NAME, Secrets.WIFI_PASSWORD)

    # Give it 30 seconds.
    for second in range(30):
        if wlan.isconnected():
            print("WiFi connected, address", wlan.ifconfig()[0])
            return
        time.sleep(1)
    raise OSError("WiFi didn't connect")


def connect_mqtt():
    client = MQTTClient(CLIENT_ID, Secrets.MQTT_BROKER, port=Secrets.MQTT_PORT,
                        user=Secrets.MQTT_USER, password=Secrets.MQTT_PASSWORD,
                        keepalive=60)
    client.set_callback(on_message)
    client.connect()
    for topic in TOPICS:
        client.subscribe(topic)
    print("MQTT connected to", Secrets.MQTT_BROKER)
    return client


def run():
    # Show PV power until Ctrl-C. If WiFi or MQTT drops, wait and start again;
    # the pointer stays where it is meanwhile.
    while True:
        try:
            connect_wifi()
            client = connect_mqtt()
            last_update = 0
            last_ping = time.time()

            while True:
                client.check_msg()            # handle any messages waiting
                now = time.time()

                if now - last_update >= UPDATE_S:
                    watts = total()
                    print("PV", watts, "W")
                    dial(watts / SCALE)
                    last_update = time.time()

                if now - last_ping >= PING_S:
                    client.ping()
                    last_ping = now

                time.sleep_ms(100)

        except Exception as error:
            print("Connection problem:", error, "- trying again in 10 s")
            time.sleep(10)


print("meter version", VERSION)
run()
