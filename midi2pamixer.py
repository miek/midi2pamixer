from pulsectl import Pulse
pulse = Pulse('midi2pamixer')
from pygame import midi
import time

def handle_mute(channel, value):
    pulse.mute(get_pulse_channel(channel), value == 127)

def handle_slider(channel, value):
    pulse.volume_set_all_chans(get_pulse_channel(channel), value / 127.0)

control_group_handlers = [
    (range(48, 56), handle_mute),
    (range(0, 8), handle_slider),
]

def get_pulse_channel(channel):
    return pulse.sink_input_list()[channel]

def handle_cc(cc, value):
    for h in control_group_handlers:
        cc_range, cc_handler = h
        if cc in cc_range:
            channel = cc - cc_range[0]
            if channel < len(pulse.sink_input_list()):
                cc_handler(channel, value)

midi.init()
inp = midi.Input(3)
while True:
    if inp.poll():
        for event in inp.read(10):
            ((status, cc, value, data3), timestamp) = event
            if status == 176:
                handle_cc(cc, value)
    time.sleep(0.01)
