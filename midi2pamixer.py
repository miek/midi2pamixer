from pulsectl import Pulse
pulse = Pulse('midi2pamixer')
from pygame import midi
import time

def handle_input(cc, value):
    if cc < 8: # slider
        if cc < len(pulse.sink_input_list()):
            sink = pulse.sink_input_list()[cc]
            pulse.volume_set_all_chans(sink, value / 127.0)

midi.init()
inp = midi.Input(3)
while True:
    if inp.poll():
        for event in inp.read(10):
            ((status, cc, value, data3), timestamp) = event
            if status == 176:
                handle_input(cc, value)
    time.sleep(0.01)
