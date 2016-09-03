from pulsectl import Pulse
pulse = Pulse('midi2pamixer')
from pygame import midi
import time

sliders = range(0, 8)

def handle_slider(channel, value):
    if channel < len(pulse.sink_input_list()):
        sink = pulse.sink_input_list()[cc]
        pulse.volume_set_all_chans(sink, value / 127.0)

def handle_cc(cc, value):
    if cc in sliders: # slider
        handle_slider(cc - sliders[0], value)

midi.init()
inp = midi.Input(3)
while True:
    if inp.poll():
        for event in inp.read(10):
            ((status, cc, value, data3), timestamp) = event
            if status == 176:
                handle_cc(cc, value)
    time.sleep(0.01)
