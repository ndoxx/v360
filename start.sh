#!/bin/sh
sudo modprobe -i uinput
sudo chmod g+rw /dev/uinput
sudo chgrp uinput /dev/uinput