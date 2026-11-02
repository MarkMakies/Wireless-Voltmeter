# pointer.py - moves the meter's pointer: the PWM output, the calibration table,
# and glide() and dial() to move to a reading. meter.py and demo.py both use it,
# so if you recalibrate, change CALIBRATION here and nowhere else.
# Copy it to the board beside main.py.
# History:
#   v3 the dial's range comes from the calibration table, not fixed at 0-600
#   v2 glide() moves without printing; dial() prints
#   v1 moved out of meter.py v7: pulsed drive, calibration, S-curve glide

import time
from machine import Pin, PWM

VERSION = 3

PWM_PIN = 25          # D25 on the DEVKIT V1 board
START_FREQ = 100      # 100 Hz pulses: each one resets the meter's iron, so the reading
                      # doesn't depend on where the pointer came from

# How long a glide takes to move the pointer, in milliseconds, and how often it
# updates the duty on the way. Longer is smoother.
GLIDE_MS = 3000
STEP_MS = 20

# Calibration: each dial reading and the duty (%) that puts the pointer on it,
# from the bottom of the dial to the top.
# Measured 2026-11-02 with the 100 Hz pulsed drive.
CALIBRATION = [
    [0, 0.0],
    [100, 8.0],
    [200, 19.5],
    [300, 33.5],
    [400, 51.7],
    [500, 71.7],
    [600, 91.8],
]

# Start the PWM output switched off (0 % duty) so nothing moves until we ask.
pwm = PWM(Pin(PWM_PIN), freq=START_FREQ, duty_u16=0)

# The duty right now, so the next glide knows where to start from.
duty_now = 0.0


def limit(percent):
    # Keep a duty between 0 and 100.
    if percent < 0:
        return 0
    if percent > 100:
        return 100
    return percent


def set_duty(percent):
    # The board counts duty from 0 (always off) to 65535 (always on).
    value = int(limit(percent) * 65535 / 100)
    pwm.duty_u16(value)


def duty(percent):
    # Jump straight to a duty, and remember it so the next glide starts from here.
    global duty_now
    percent = limit(percent)
    set_duty(percent)
    duty_now = percent
    print("Duty", percent, "%")


def reading_to_duty(reading):
    # Keep the reading on the dial: between the first and last marks in the table.
    bottom = CALIBRATION[0][0]
    top = CALIBRATION[len(CALIBRATION) - 1][0]
    if reading < bottom:
        reading = bottom
    if reading > top:
        reading = top

    # Find the two calibration points either side of the reading,
    # and draw a straight line between them.
    for i in range(len(CALIBRATION) - 1):
        low_reading = CALIBRATION[i][0]
        low_duty = CALIBRATION[i][1]
        high_reading = CALIBRATION[i + 1][0]
        high_duty = CALIBRATION[i + 1][1]
        if reading <= high_reading:
            fraction = (reading - low_reading) / (high_reading - low_reading)
            return low_duty + fraction * (high_duty - low_duty)


def glide(reading):
    # Glide the pointer to a reading on the dial.
    global duty_now
    start = duty_now
    target = reading_to_duty(reading)
    steps = GLIDE_MS // STEP_MS

    # Follow an S-shaped curve: slow start, quicker middle, slow finish.
    for step in range(1, steps + 1):
        f = step / steps                      # how far through the glide, 0 to 1
        shape = 3 * f * f - 2 * f * f * f     # the S-curve: 0 at the start, 1 at the end
        duty_now = start + (target - start) * shape
        set_duty(duty_now)
        time.sleep_ms(STEP_MS)


def dial(reading):
    # Glide, then show the reading and the duty it needed.
    glide(reading)
    print("Dial", reading, "-> duty", round(reading_to_duty(reading), 1), "%")


def freq(hz):
    pwm.freq(hz)
    # The board picks the nearest frequency it can make, so show what it chose.
    print("Frequency", pwm.freq(), "Hz")


print("pointer version", VERSION)
