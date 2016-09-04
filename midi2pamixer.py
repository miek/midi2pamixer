import mido
from pulsectl import Pulse
import time
pulse = Pulse('midi2pamixer')
mido.set_backend('mido.backends.rtmidi')

channels = []

class channel:
    def __init__(self, channel_id, sink_index):
        self.channel_id, self.sink_index = channel_id, sink_index
        sink = self.get_sink()
        self.set_mute(sink.mute == 1)

    def get_sink(self):
        return get_sink_by_index(self.sink_index)

    def set_led(self, led, on):
        chan = self.channel_id + control_groups[led][0]
        msg = mido.Message('control_change', control=chan, value=127 if on else 0)
        midi_output.send(msg)

    def set_mute(self, mute):
        pulse.mute(self.get_sink(), mute)
        self.muted = mute
        self.set_led('mute', self.muted)

    def toggle_mute(self):
        self.set_mute(not self.muted)

    def set_volume(self, volume):
        pulse.volume_set_all_chans(self.get_sink(), volume)


def handle_button(channel, control, value):
    value = value == 127
    if control == 'mute':
        if value:
            channel.toggle_mute()

def handle_analog(channel, control, value):
    value = value / 127.0
    if control == 'slider':
        channel.set_volume(value)

control_groups = {
    'slider': (0,  handle_analog),
    'knob':   (16, handle_analog),
    'solo':   (32, handle_button),
    'mute':   (48, handle_button),
    'rec':    (64, handle_button),
}

def get_sink_by_channel(channel):
    return pulse.sink_input_list()[channel]

def get_sink_by_index(index):
    return filter(lambda x: x.index == index, pulse.sink_input_list())[0]

def handle_cc(cc, value):
    for key, cg in control_groups.items():
        cc_offset, cc_handler = cg
        if cc in range(cc_offset, cc_offset+8):
            channel = cc - cc_offset
            if channel < len(pulse.sink_input_list()):
                cc_handler(channels[channel], key, value)

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
