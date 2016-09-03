import mido
from pulsectl import Pulse
import time
pulse = Pulse('midi2pamixer')
mido.set_backend('mido.backends.rtmidi')

def handle_mute(channel, value):
    pulse.mute(get_pulse_channel(channel), value == 127)
    msg = mido.Message('control_change', control=channel+48, value=value)
    midi_output.send(msg)

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

midi_input = mido.open_input("nanoKONTROL2 36:0")
midi_output = mido.open_output("nanoKONTROL2 36:0")
while True:
    for msg in midi_input.iter_pending():
        if msg.type == 'control_change':
            handle_cc(msg.control, msg.value)
    time.sleep(0.01)
