import threading
from queue import Queue
import servo
import stepper_motor
import camera_dashboard

def main():
    q = Queue()
    threading.Thread(target=servo.servo_control, args=(q,), daemon=True).start()
    threading.Thread(target=stepper_motor.stepper_loop, daemon=True).start()
    camera_dashboard.start_dashboard(q)

if __name__ == "__main__":
    main()
