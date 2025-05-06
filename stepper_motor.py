import RPi.GPIO as GPIO
import time

IN1, IN2, IN3, IN4 = 4, 5, 6, 13
pins = [IN1, IN2, IN3, IN4]
half_step_seq = [
    [1,0,0,0], [1,1,0,0], [0,1,0,0], [0,1,1,0],
    [0,0,1,0], [0,0,1,1], [0,0,0,1], [1,0,0,1]
]
STEPS_PER_DEGREE = 512 / 360

def rotate(degrees, delay=0.001):
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
        GPIO.output(pin, False)

    try:
        while True:
            rotate(90)     # 0 → 90°
            time.sleep(8)  # Stay 8s
            rotate(90)     # 90 → 180°
            time.sleep(3)  # Stay 3s
            time.sleep(2)  # Pause before return
            rotate(-180)   # Back to 0°
    finally:
        GPIO.cleanup()
