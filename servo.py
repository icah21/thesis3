# servo.py
import RPi.GPIO as GPIO
import time

def set_servo_angle(pwm, angle):
    duty = 2.5 + (angle / 18.0)
    pwm.ChangeDutyCycle(duty)

def servo_control(queue):
    GPIO.setmode(GPIO.BCM)
    servo_pin = 18
    GPIO.setup(servo_pin, GPIO.OUT)

    pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz
    pwm.start(0)
    print("Servo ready.")

    try:
        while True:
            if not queue.empty():
                label = queue.get()
                print(f"Servo received: {label}")
                angle = {
                    "Criollo": 45,
                    "Forastero": 90,
                    "Trinitario": -45,
                }.get(label, 0)

                set_servo_angle(pwm, angle)
                time.sleep(5)
                set_servo_angle(pwm, 0)
                time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        pwm.stop()
        GPIO.cleanup()
