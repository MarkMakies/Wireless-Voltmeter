# demo.py - demo mode: the pointer acts out a day of solar power. No WiFi needed.
# Sunrise to a midday peak and back to sunset in about 2 minutes, with the odd
# cloud passing over, then a short night, over and over. Good for showing the
# meter off, or testing it before MQTT.
# Needs pointer.py on the board. To try it, Ctrl-C the meter at the console and type:
#   import demo
# To start in demo mode at power-up, copy it to the board as main.py instead of meter.py.
# Ctrl-C stops it.
# History:
#   v3 quieter: prints only sunrise, clouds and sunset
#   v2 clouds
#   v1 first version: a fake PV day

import time
import math
import random
from pointer import glide, dial, duty, freq   # dial, duty and freq are for the console

VERSION = 3

PEAK = 550            # midday high on the dial; about 90 % of the top suits any dial
STEPS = 40            # pointer moves per day; each takes 3 s, so a day lasts 2 minutes
NIGHT_S = 10          # seconds of darkness between days
CLOUD_CHANCE = 15     # % chance a cloud arrives at each move
CLOUD_MOVES = 4       # a cloud lasts 1 to this many moves


def day():
    # One day of sunshine. The power rises and falls like the top half of a
    # sine wave: 0 at sunrise, PEAK at midday, 0 again at sunset.
    print("Sunrise")
    cloud_left = 0                                # moves left of the current cloud
    shade = 100                                   # % of the sun the cloud lets through
    for step in range(STEPS + 1):
        f = step / STEPS                          # how far through the day, 0 to 1
        sun = PEAK * math.sin(math.pi * f)

        # Now and then a cloud drifts over and cuts the power for a few moves.
        if cloud_left == 0 and random.randint(1, 100) <= CLOUD_CHANCE:
            cloud_left = random.randint(1, CLOUD_MOVES)
            shade = random.randint(20, 60)
            print("Cloud")

        if cloud_left > 0:
            reading = sun * shade / 100
            cloud_left = cloud_left - 1
        else:
            reading = sun

        glide(reading)
    print("Sunset")


def run():
    # Day after day until Ctrl-C.
    while True:
        day()
        time.sleep(NIGHT_S)


print("demo version", VERSION)
run()
