# Code für BerkelBike Sensor:
import time
import threading
from random import randint

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Das Modul 'RPi.GPIO' konnte nicht importiert werden. GPIO ist nicht verfügbar.")
    GPIO = None

from rpm_calculator import RPMCalculator


class CadenceSensorManager(object):
    def __init__(self):
        self._stop_event = threading.Event()
        self.sensor_thread = None
        self.rpm_calculator = RPMCalculator()
        self.last_valid_rpm = 0

        if GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            self.__port_CHN = 22
            self.Counter = 0
            self.CrankAngle = 0
            self.can_count = False

            # CHA und CHB ruhig stellen
            CHA_PIN = 5
            CHB_PIN = 6
            GPIO.setup(CHA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(CHB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            GPIO.setup(self.__port_CHN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(self.__port_CHN, GPIO.RISING, callback=self.__ENCODER_CHN_callback, bouncetime=5)
        else:
            self.Counter = 0

    def __ENCODER_CHN_callback(self, channel):
        now = time.perf_counter()  # Aktuelle Zeit (hohe Auflösung)

        self.last_chn_time = now  # Zeit des letzten gültigen Impulses merken

        #self.CrankAngle = 0
        self.Counter += 1
        #print(f"⚡️ CHN erkannt! Counter: {self.Counter} bei {now: .6f}")
        self.rpm_calculator.increment_rounds()

    def reset(self):
        self.Counter = 0

    def get_Counter(self):
        return self.Counter

    def get_cadence(self):
        now = time.perf_counter()

        if self.rpm_calculator.last_round_time and (now - self.rpm_calculator.last_round_time) < 4.0:
            raw_rpm = round(self.rpm_calculator.get_rpm())
            if raw_rpm > 10:
                self.last_valid_rpm = raw_rpm  # Letzten sinnvollen Wert merken
            return self.last_valid_rpm
        else:
            return 0  # Wenn länger keine Aktivität, dann trotzdem auf 0
        
    def start_SensorRead(self):
        self._stop_event.clear()


    def stop(self):
        self._stop_event.set()
        if not GPIO:
            return
        GPIO.cleanup()
