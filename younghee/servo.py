import pigpio
import time
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

class Servo:
    """Operates each of the servos to their calibrated open/close position"""

    def __init__(self):
        try:
            self.pwm = pigpio.pi()
            self.servo = 18

            self.pwm.set_mode(self.servo, pigpio.OUTPUT)
            self.pwm.set_PWM_frequency(self.servo, 100)
            self.turn_forwards()
            logging.info("Servo initialized")
        except Exception as e:
            logging.error(f"Error initializing servo: {e}")

    def turn_forwards(self):
        try:
            logging.info("Turning servo forwards")
            self.pwm.set_servo_pulsewidth(self.servo, 2400)
            time.sleep(3)
            self.pwm.set_servo_pulsewidth(self.servo, 0)
        except Exception as e:
            logging.error(f"Error turning servo forwards: {e}")

    def turn_halfway(self):
        try:
            logging.info("Turning servo halfway")
            self.pwm.set_servo_pulsewidth(self.servo, 1500)
            self.pwm.set_servo_pulsewidth(self.servo, 0)
        except Exception as e:
            logging.error(f"Error turning servo halfway: {e}")

    def turn_backwards(self):
        try:
            logging.info("Turning servo backwards")
            self.pwm.set_servo_pulsewidth(self.servo, 500)
            self.pwm.set_servo_pulsewidth(self.servo, 0)
        except Exception as e:
            logging.error(f"Error turning servo backwards: {e}")

    def stop(self):
        try:
            logging.info("Stopping servo")
            self.pwm.set_servo_pulsewidth(self.servo, 0)
            self.pwm.stop()
        except Exception as e:
            logging.error(f"Error stopping servo: {e}")

if __name__ == "__main__":
    servo = Servo()
    servo.turn_forwards()
    servo.turn_backwards()
    servo.stop()