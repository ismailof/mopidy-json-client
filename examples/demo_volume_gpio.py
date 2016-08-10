#!/usr/bin/python

from mopidy_json_client import MopidyClient
from gpio_controls import RotaryEncoder, MomentarySwitch
from time import sleep


class VolumeGPIO(object):

    mopidy = MopidyClient()
    volume = 50
    mute = False

    def __init__(self, pinout):

        # Bind mopidy events to functions
        self.mopidy.listener.bind('volume_changed', self.update_volume)
        self.mopidy.listener.bind('mute_changed', self.update_mute)

        # Get initial values for volume and mute
        self.mopidy.mixer.get_volume(on_result=self.update_volume)
        self.mopidy.mixer.get_mute(on_result=self.update_mute)

        # Initialize GPIO controlers
        self.c_volume = RotaryEncoder(pinout=(pinout[0], pinout[1]),
                                      on_rotate=self.change_volume)

        self.c_mute = MomentarySwitch(pin=pinout[2],
                                      holdtime=2,
                                      on_press=self.toggle_mute)

    def change_volume(self, value):
        new_volume = max(min(self.volume + value * 5, 100), 0)
        self.mopidy.mixer.set_volume(new_volume)

    def toggle_mute(self):
        new_mute = not self.mute
        self.mopidy.mixer.set_mute(new_mute)

    def update_volume(self, volume):
        self.volume = volume

    def update_mute(self, mute):
        self.mute = mute

    def close(self):
        self.c_volume.close()
        self.c_mute.close()


if __name__ == '__main__':

    # GPIO pins of the Rotary Control
    ROTARY_A = 13
    ROTARY_B = 19
    ROTARY_S = 26

    # Initialize example
    c_volume = VolumeGPIO(pinout=(ROTARY_A, ROTARY_B, ROTARY_S))

    # Main loop
    try:
        while True:
            sleep(0.2)
    except KeyboardInterrupt:
        pass

#    c_volume.close()
#    exit(0)
