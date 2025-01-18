import pigpio
import time

class Servo:
    """Operates each of the servos to their calibrated open/close position"""

    def __init__(self):
        try:
            self.pwm = pigpio.pi()
            self.servo = 18

            self.pwm.set_mode(self.servo, pigpio.OUTPUT)
            self.pwm.set_PWM_frequency(self.servo, 50)
            self.turn_forwards()

        except Exception as e:
            print(e)
            return

    def turn_forwards(self):
        self.pwm.set_servo_pulsewidth(self.servo, 2500)
        time.sleep(1)
        self.pwm.set_servo_pulsewidth(self.servo, 0)

    def turn_backwards(self):
        self.pwm.set_servo_pulsewidth(self.servo, 500)
        time.sleep(1)
        self.pwm.set_servo_pulsewidth(self.servo, 0)

if __name__ == "__main__":
    servo = Servo()
    servo.turn_forwards()
    time.sleep(1)
    servo.turn_backwards()