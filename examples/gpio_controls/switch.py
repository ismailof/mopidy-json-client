from RPi import GPIO
from threading import Thread, Timer
from time import sleep


class MomentarySwitch(object):

    _pushed = False
    long_timer = None

    def __init__(self, pin,
                 holdtime=0,
                 on_press=None,
                 on_hold=None,
                 on_push=None,
                 on_release=None):

        self.pin = pin

        self.holdtime = holdtime
        self._cb_press = on_press
        self._cb_hold = on_hold
        self._cb_push = on_push
        self._cb_release = on_release

        # Set GPIO PINs as output with pull-up
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin,
                              GPIO.BOTH,
                              callback=self.on_switch_edge,
                              bouncetime=150)

    def __exit__(self):
        self.close()

    def close(self):
        GPIO.cleanup(self.pin)

    def on_switch_edge(self, pin):
        sleep(0.1)
        if not GPIO.input(pin):
            self.push()
        else:
            self.release()

    def push(self):
        if self._cb_push:
            Thread(target=self._cb_push).start()

        self._pushed = True
        if self.holdtime:
            self.long_timer = Timer(self.holdtime, self.hold)
            self.long_timer.start()

    def release(self):
        if self._cb_release:
            Thread(target=self._cb_release).start()

        if self.long_timer:
            self.long_timer.cancel()
        if self._pushed:
            self.press()
        self._pushed = False

    def press(self):
        if self._cb_press:
            Thread(target=self._cb_press).start()

    def hold(self):
        if self._cb_hold and self._pushed:
            Thread(target=self._cb_hold).start()

        self._pushed = False
