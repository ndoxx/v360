from evdev import events, ecodes, UInput, AbsInfo
import numpy as np


KEYMAP = {
    'BtnA':         (events.EV_KEY, ecodes.BTN_A),
    'BtnB':         (events.EV_KEY, ecodes.BTN_B),
    'BtnX':         (events.EV_KEY, ecodes.BTN_X),
    'BtnY':         (events.EV_KEY, ecodes.BTN_Y),
    'BtnBack':      (events.EV_KEY, ecodes.BTN_SELECT),
    'BtnStart':     (events.EV_KEY, ecodes.BTN_START),
    'BtnShoulderL': (events.EV_KEY, ecodes.BTN_TL),
    'BtnShoulderR': (events.EV_KEY, ecodes.BTN_TR),
    'LeftX':        (events.EV_ABS, ecodes.ABS_X),
    'LeftY':        (events.EV_ABS, ecodes.ABS_Y),
    'TriggerL':     (events.EV_ABS, ecodes.ABS_Z),
    'TriggerR':     (events.EV_ABS, ecodes.ABS_RZ),
    'DpadX':        (events.EV_ABS, ecodes.ABS_HAT0X),
    'DpadY':        (events.EV_ABS, ecodes.ABS_HAT0Y),
}

ABSINFO = {
    'LeftX':    AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0),
    'LeftY':    AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0),
    'TriggerL': AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0),
    'TriggerR': AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0),
    'DpadX':    AbsInfo(value=0, min=-128, max=127, fuzz=0, flat=0, resolution=0),
    'DpadY':    AbsInfo(value=0, min=-128, max=127, fuzz=0, flat=0, resolution=0),
}

DPAD_TO_KEY_VAL = {
    1: ("DpadY", -1),
    2: ("DpadY", 1),
    4: ("DpadX", -1),
    8: ("DpadX", 1),
}


def analog_remap(value, min_val, max_val, centered: bool):
    # Clamp value
    value = (1 + max(-1, min(1, value))) / \
        2 if centered else max(0, min(1, value))
    # Translate and rescale
    return int(min_val+(max_val-min_val)*value)


class VirtualController():
    def __init__(self):
        key_events = [tup[1]
                      for tup in KEYMAP.values() if tup[0] == events.EV_KEY]

        abs_events = [(it[1][1], ABSINFO[it[0]])
                      for it in KEYMAP.items() if it[1][0] == events.EV_ABS]

        handled_events = {
            ecodes.EV_KEY: key_events,
            ecodes.EV_ABS: abs_events
        }

        self.device = UInput(handled_events, name="v360")
        print(self.device)

    def send(self, key, value):
        event_type, key_code = KEYMAP[key]

        # Clamp and rescale analog values
        if event_type == events.EV_ABS:
            # Trigger values are not centered (in [0,1])
            is_trigger = key == "TriggerL" or key == "TriggerR"
            value = analog_remap(
                value, ABSINFO[key].min, ABSINFO[key].max, not is_trigger)

        self.device.write(event_type, key_code, value)
        self.device.syn()


class FFXController:
    def __init__(self):
        self.gamepad = VirtualController()

    def set_value(self, xKey, value):
        # Sanity check
        if xKey == "AxisLx" or xKey == "AxisLy":
            print(f"ERROR - OLD MOVEMENT COMMAND FOUND: {xKey}")
            self.set_neutral()

        # Dpad and triggers handled like buttons (on/off control)
        if xKey == "Dpad":
            xKey, value = DPAD_TO_KEY_VAL[value]

        # Press and release
        self.gamepad.send(xKey, value)
        self.gamepad.send(xKey, 0)

    def set_movement(self, x, y):
        self.gamepad.send("LeftX", x)
        self.gamepad.send("LeftY", y)

    def set_neutral(self):
        # Only the left stick needs be reset
        self.gamepad.send("LeftX", 0)
        self.gamepad.send("LeftY", 0)
