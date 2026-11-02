# SecretsExample.py
# Shows what goes in Secrets.py. Copy this file to Secrets.py, put in your own
# values, then copy Secrets.py to the board:
#   mpremote cp Secrets.py :Secrets.py
# Secrets.py never goes into git.

# Your WiFi network
WIFI_NAME = "your-wifi-name"
WIFI_PASSWORD = "your-wifi-password"

# Your MQTT broker (the computer that passes messages around)
MQTT_BROKER = "192.168.1.10"
MQTT_PORT = 1883
MQTT_USER = "your-mqtt-user"
MQTT_PASSWORD = "your-mqtt-password"

# What to show: the MQTT topics whose numbers get added up (one is fine)
TOPICS = [
    "home/solar/power",
]
