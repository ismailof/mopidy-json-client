from RPi import GPIO
from threading import Thread, Lock


class RotaryEncoder(object):

    RIGHT = +1
    LEFT = -1

    _lock = Lock()
    last_state = (True, True)

    def __init__(self, pinout, on_rotate=None):
        self.pinA = pinout[0]
        self.pinB = pinout[1]
        self._callback = on_rotate

        # GPIO mode: use the GPIOn number
        GPIO.setmode(GPIO.BCM)

        # Init GPIO inputs
        for pin in [self.pinA, self.pinB]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin,
                                  GPIO.RISING,
                                  callback=self.on_rotary_edge,
                                  bouncetime=10)

    def on_rotary_edge(self, pin):
        current_state = (GPIO.input(self.pinA),
                         GPIO.input(self.pinB))

        if current_state == self.last_state:
            return

        self._lock.acquire()
        self.last_state = current_state

        if all(current_state):
            event = self.RIGHT if pin == self.pinB \
                else self.LEFT

            if self._callback:
                Thread(target=self._callback, args=(event,)).start()

        self._lock.release()

    def close(self):
        GPIO.cleanup([self.pinA, self.pinB])

    def __exit__(self):
        self.close()
