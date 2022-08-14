from evdev import events, ecodes, UInput, AbsInfo

# Associate control names to event type and key code
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

# Associate analog control names to AbsInfo structures to specify range and behavior
ABSINFO = {
    'LeftX':    AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0),
    'LeftY':    AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0),
    'TriggerL': AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0),
    'TriggerR': AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0),
    'DpadX':    AbsInfo(value=0, min=-128, max=127, fuzz=0, flat=0, resolution=0),
    'DpadY':    AbsInfo(value=0, min=-128, max=127, fuzz=0, flat=0, resolution=0),
}

# Associate Dpad binary mask to axis and direction
DPAD_TO_KEY_VAL = {
    1: ("DpadY", -1),
    2: ("DpadY", 1),
    4: ("DpadX", -1),
    8: ("DpadX", 1),
}


def analog_remap(value, min_val, max_val, centered: bool):
    """
    Remap a centered value (in [-1,1]) or a non-centered
    value (in [0,1]) to the interval [min_val, max_val].
    Values are first clamped between -1 and 1 if centered
    or 0 and 1 if not centered.
    """
    # Clamp value
    value = (1 + max(-1, min(1, value))) / \
        2 if centered else max(0, min(1, value))
    # Translate and rescale
    return int(min_val+(max_val-min_val)*value)


class VirtualController():
    """
    This class creates a UInput device and allows to send
    events to it.
    """

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
    """
    Linux compatible drop-in replacement for FFX_Xbox.vgTranslator.
    """

    def __init__(self):
        self.gamepad = VirtualController()

    def set_value(self, xKey, value):
        # Sanity check
        if xKey == "AxisLx" or xKey == "AxisLy":
            print(f"ERROR - OLD MOVEMENT COMMAND FOUND: {xKey}")
            self.set_neutral()

        # Dpad handled like buttons (on/off control)
        if xKey == "Dpad":
            if value != 0:
                xKey, value = DPAD_TO_KEY_VAL[value]
            else:
                self.gamepad.send("DpadX", 0)
                self.gamepad.send("DpadY", 0)
                return

        # Press or release
        self.gamepad.send(xKey, value)

    def set_movement(self, x, y):
        # Update left stick value
        self.gamepad.send("LeftX", x)
        self.gamepad.send("LeftY", y)

    def set_neutral(self):
        for key in KEYMAP.keys():
            self.gamepad.send(key, 0)
