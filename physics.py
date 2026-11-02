# physics.py - for filming the physics: the needle jumps between two readings,
# then glides between the same two along the S-curve. The jumps overshoot and
# swing; the glides arrive without a wobble.
# Needs pointer.py on the board. Ctrl-C the meter at the console and type:
#   import physics
# Each run takes about 38 seconds, after a 5 second wait. It repeats for
# another take until Ctrl-C.
# History:
#   v4 9 seconds after a jump
#   v3 7 second waits
#   v2 5 second waits: the swings were still going at the next move
#   v1 first version: jumps, then S-curve glides

import time
from pointer import glide, duty, reading_to_duty

VERSION = 4

LOW = 200             # the two readings to move between
HIGH = 400
JUMP_WAIT_S = 9       # after a jump: long enough to watch the swings die away
GLIDE_WAIT_S = 7      # after a glide: nothing to see, it's already still
AGAIN_S = 5           # wait before each run: time to start filming


def jump(reading):
    # Straight to the new reading in one go, no S-curve.
    duty(reading_to_duty(reading))


def run():
    # Settle on LOW first, so the first run starts from rest.
    glide(LOW)
    while True:
        print("Ready")
        time.sleep(AGAIN_S)

        # Jumps: the needle overshoots, swings back short, and wobbles.
        print("Jumps")
        jump(HIGH)
        time.sleep(JUMP_WAIT_S)
        jump(LOW)
        time.sleep(JUMP_WAIT_S)

        # The same moves along the S-curve: no wobble.
        print("S-curve")
        glide(HIGH)
        time.sleep(GLIDE_WAIT_S)
        glide(LOW)
        time.sleep(GLIDE_WAIT_S)


print("physics version", VERSION)
run()
