# python-uinput

`python-uinput` was installed from source:

```
git clone https://github.com/tuomasjjrasanen/python-uinput
cd python-uinput
python3 setup.py build
sudo python3 setup.py install
```

Then we need to load the uinput kernel module:

```
sudo modprobe uinput
```

To make it permanent (which I won't do for security reasons), it is advised to:

```
sudo nano /etc/modules
> uinput
> Ctrl+X
```

On testing the keyboard sample, I don't see anything written (should write HELLO). But, launching it from a virtual terminal (Ctrl+Alt+F3), it works (see [1]).

I'm installing the `evtest` package for diagnostics:

```
sudo apt-get install evtest
```

Well, seems I'm not needing it for now, bc I made it work. I just wait a bit before event emission, and it seems to work. Tested mouse control sample too.

```python
def test_mouse():
    with uinput.Device([uinput.REL_X, uinput.REL_Y,
                        uinput.BTN_LEFT, uinput.BTN_RIGHT]) as device:
        time.sleep(1)
        for i in range(20):
            device.emit(uinput.REL_X, 5)
            device.emit(uinput.REL_Y, 5)
```

This suggests that the device input file is not yet ready when opened. In [1] people report the same problem, and it seems that device creation is non-blocking, which would explain everything.


No need to execute as root, strangely. If somehow needed in the future, this should allow me to write to /dev/uinput freely:

```
sudo groupadd uinput
sudo usermod -a -G uinput "$USER"
sudo chmod g+rw /dev/uinput
sudo chgrp uinput /dev/uinput
```

But note that:
"...after a reboot, permissions and group ownership on /dev/uinput resets. You may have to run chmod and chgrp commands at startup with a cronjob hoping /dev/uinput is already created by the kernel driver by the time cronjob runs."

So I added the last two lines to my `start.sh` (already performing the modprobe).


# evdev

An alternative is to use the evdev module, which can among other things talk to uinput.

```
pip3 install evdev
```

[3] Is an XBox360 controller implementation that can remap a controller with a similar layout to an XBox360 one. Source code is in [4]. I should take this as inspiration to build a virtual controller. The edev doc is in [5].

Seems to work fine. 



# Virtual gamepad

Let's simulate a fucking XBox360 gamepad then.

From [2], there is a short guide on how to pose as an XBox360 controller using the xboxdrv driver. It should remap the controls to the appropriate linux events.
```
$ xboxdrv --evdev /dev/input/event* --evdev-absmap ABS_X=X1,ABS_Y=Y1,ABS_RX=X2,ABS_RY=Y2 --evdev-keymap BTN_DPAD_UP=du,BTN_DPAD_DOWN=dd,BTN_DPAD_LEFT=dl,BTN_DPAD_RIGHT=dr,BTN_SELECT=back,BTN_MODE=guide,BTN_START=start,BTN_TL=TL,BTN_TR=TR,BTN_EAST=A,BTN_SOUTH=B,BTN_NORTH=X,BTN_WEST=Y,BTN_THUMBL=LB,BTN_THUMBR=RB,BTN_TL2=LT,BTN_TR2=RT --axismap -Y1=Y1,-Y2=Y2
```

In /usr/include/linux/input-event-codes.h the corresponding linux events are listed here:
```
axis:    ABS_X, ABS_Y, ABS_Z, ABS_RX, ABS_RY, ABS_RZ, ABS_HAT0X, ABS_HAT0Y
buttons: BTN_A, BTN_B, BTN_X, BTN_Y, BTN_TL, BTN_TR, BTN_SELECT, BTN_START, BTN_MODE, BTN_THUMBL, BTN_THUMBR
```

## Working?

My strategy is to code a drop-in replacement for `FFX_Xbox.vgTranslator`. That's the `v360.FFXController` that internally uses a custom `v360.VirtualController` virtual gamepad (subset of layout of XBox360 gamepad). The virtual gamepad uses `evdev` to create a uinput device, and can send events to it. The code is data-oriented.

I wrote a small test program to see if it works:

```python
from v360 import FFXController
import time

def main(argv):
    ctl = FFXController()

    input("Launch evtest and press <ENTER>.")

    for i in range(10):
        ctl.set_value("BtnA", 1)
        ctl.set_value("BtnB", 1)
        ctl.set_value("BtnX", 1)
        ctl.set_value("BtnY", 1)
        time.sleep(1)
```
I run this on terminal A. On terminal B, I can `sudo evtest` and look for the device "v360", then switch back to term A and press enter. Now the test program sends button events regularly, and I can see them captured by evtest. So it does work.

## What I don't know

* The ranges in the `AbsInfo` structures for the analog controls. I don't know how to scale them properly, and I don't know if they accept negative values (I guess not).



# Sources
[1] https://github.com/tuomasjjrasanen/python-uinput/issues/6
[2] https://wiki.archlinux.org/title/Gamepad
[3] https://pypi.org/project/ubox360/
[4] https://gitlab.com/albinou/python-ubox360/-/blob/master/src/ubox360/ubox360.py
[5] https://python-evdev.readthedocs.io/en/latest/index.html