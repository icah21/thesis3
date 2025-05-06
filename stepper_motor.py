# stepper_motor.py
import RPi.GPIO as GPIO
import time

# GPIO pin setup for ULN2003
IN1 = 4
IN2 = 5
IN3 = 6
IN4 = 13
pins = [IN1, IN2, IN3, IN4]

# 8-step half stepping sequence
half_step_seq = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1]
]

STEPS_PER_REV = 512  # 28BYJ-48: 512 steps per full rotation
DEGREES_PER_REV = 360
STEPS_PER_DEGREE = STEPS_PER_REV / DEGREES_PER_REV

def rotate(degrees, delay=0.002):
    steps = int(STEPS_PER_DEGREE * abs(degrees))
    direction = 1 if degrees > 0 else -1

    for _ in range(steps):
        for step in range(8)[::direction]:
            for pin in range(4):
                GPIO.output(pins[pin], half_step_seq[step][pin])
            time.sleep(delay)

def stepper_loop():
    GPIO.setmode(GPIO.BCM)
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

    try:
        while True:
            rotate(90)      # 0 -> 90
            time.sleep(5)
            rotate(90)      # 90 -> 180
            time.sleep(5)
            rotate(-180)    # 180 -> 0
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
