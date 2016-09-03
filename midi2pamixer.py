import mido
from pulsectl import Pulse
import time
pulse = Pulse('midi2pamixer')
mido.set_backend('mido.backends.rtmidi')

channels = []

class channel:
    def __init__(self, channel_id, sink_index):
        self.channel_id, self.sink_index = channel_id, sink_index
        print(self.get_sink())

    def get_sink(self):
        return get_sink_by_index(self.sink_index)


def handle_mute(channel, value):
    pulse.mute(get_sink_by_channel(channel), value == 127)
    msg = mido.Message('control_change', control=channel+48, value=value)
    midi_output.send(msg)
    print(channels[channel].get_sink())

def handle_slider(channel, value):
    pulse.volume_set_all_chans(get_sink_by_channel(channel), value / 127.0)

control_group_handlers = [
    (range(48, 56), handle_mute),
    (range(0, 8), handle_slider),
]

def get_sink_by_channel(channel):
    return pulse.sink_input_list()[channel]

def get_sink_by_index(index):
    return filter(lambda x: x.index == index, pulse.sink_input_list())[0]

def handle_cc(cc, value):
    for h in control_group_handlers:
        cc_range, cc_handler = h
        if cc in cc_range:
            channel = cc - cc_range[0]
            if channel < len(pulse.sink_input_list()):
                cc_handler(channel, value)

def handle_pulse_event(event):
    print('Pulse event', event)

midi_input = mido.open_input("nanoKONTROL2 36:0")
midi_output = mido.open_output("nanoKONTROL2 36:0")
pulse.event_mask_set('all')
pulse.event_callback_set(handle_pulse_event)

# Set up initial channels
for chan_id, sink in enumerate(pulse.sink_input_list()):
    channels.append(channel(chan_id, sink.index))

while True:
    for msg in midi_input.iter_pending():
        if msg.type == 'control_change':
            handle_cc(msg.control, msg.value)
    pulse.event_listen(0.001)
