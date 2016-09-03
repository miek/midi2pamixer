from pulsectl import Pulse
pulse = Pulse('midi2pamixer')
from pygame import midi
import time

sliders = range(0, 8)

def get_pulse_channel(channel):
    if channel < len(pulse.sink_input_list()):
        return pulse.sink_input_list()[cc]

def handle_slider(sink, value):
    pulse.volume_set_all_chans(sink, value / 127.0)

def handle_cc(cc, value):
    if cc in sliders: # slider
        sink = get_pulse_channel(cc - sliders[0])
        if sink:
            handle_slider(sink, value)

midi.init()
inp = midi.Input(3)
while True:
    if inp.poll():
        for event in inp.read(10):
            ((status, cc, value, data3), timestamp) = event
            if status == 176:
                handle_cc(cc, value)
    time.sleep(0.01)
