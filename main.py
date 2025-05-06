# main.py
import threading
from queue import Queue
import servo
import stepper_motor
import camera_dashboard

def main():
    q = Queue()

    # Start servo control
    threading.Thread(target=servo.servo_control, args=(q,), daemon=True).start()

    # Start stepper motor rotation loop
    threading.Thread(target=stepper_motor.stepper_loop, daemon=True).start()

    # Launch camera dashboard GUI
    camera_dashboard.start_dashboard(q)

if __name__ == "__main__":
    main()
