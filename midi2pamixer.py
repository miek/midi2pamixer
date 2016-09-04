import mido
from queue import Queue
from pulsectl import Pulse
import time
pulse = Pulse('midi2pamixer')
mido.set_backend('mido.backends.rtmidi')

channels = []
pulse_events = Queue()

class channel:
    def __init__(self, channel_id, sink_index):
        self.channel_id, self.sink_index = channel_id, sink_index
        sink = self.get_sink()

        self.update_muted(sink.mute == 1)
        self.set_led('rec', True)

    def __del__(self):
        self.clear_leds()

    def change_event(self):
        sink = self.get_sink()
        self.update_muted(sink.mute == 1)

    def clear_leds(self):
        self.set_led('mute', False)
        self.set_led('rec', False)

    def get_sink(self):
        return get_sink_by_index(self.sink_index)

    def set_id(self, channel_id):
        if channel_id != self.channel_id:
            # Clear up old state
            self.clear_leds()

            # Move to new chan and set state
            self.channel_id = channel_id
            self.update_muted(self.muted)
            self.set_led('rec', True)

    def set_led(self, led, on):
        chan = self.channel_id + control_groups[led][0]
        set_led(chan, on)

    def set_mute(self, mute):
        pulse.mute(self.get_sink(), mute)
        self.update_muted(mute)

    def toggle_mute(self):
        self.set_mute(not self.muted)

    def set_volume(self, volume):
        pulse.volume_set_all_chans(self.get_sink(), volume)

    def update_muted(self, muted):
        self.muted = muted
        self.set_led('mute', self.muted)

def clear_leds():
    offsets = [control_groups[button][0] for button in ['solo', 'mute', 'rec']]
    for offset in offsets:
        for control in range(offset, offset +  8):
            set_led(control, False)

def set_led(chan, on):
    msg = mido.Message('control_change', control=chan, value=127 if on else 0)
    midi_output.send(msg)

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

def get_channel_by_index(index):
    return filter(lambda x: x.sink_index == index, channels)[0]

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
    pulse_events.put(event)

def process_pulse_events():
    while not pulse_events.empty():
        event = pulse_events.get()
        print(event)
        if event.facility == 'sink_input':
            if event.t == 'new':
                channels.append(channel(len(channels), event.index))
            else:
                chan = get_channel_by_index(event.index)
                if event.t == 'change':
                    chan.change_event()
                elif event.t == 'remove':
                    del channels[chan.channel_id]
                    for key, chan in enumerate(channels):
                        chan.set_id(key)

        pulse_events.task_done()

midi_input = mido.open_input("nanoKONTROL2 36:0")
midi_output = mido.open_output("nanoKONTROL2 36:0")
pulse.event_mask_set('all')
pulse.event_callback_set(handle_pulse_event)

clear_leds()

# Set up initial channels
for chan_id, sink in enumerate(pulse.sink_input_list()):
    channels.append(channel(chan_id, sink.index))

while True:
    for msg in midi_input.iter_pending():
        if msg.type == 'control_change':
            handle_cc(msg.control, msg.value)
    pulse.event_listen(0.001)
    process_pulse_events()
