#!/usr/bin/python3
import sys
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


if __name__ == '__main__':
    main(sys.argv[1:])
