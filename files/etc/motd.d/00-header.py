#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (c) 2017 Fabrizio Colonna <colofabrix@tin.it>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import print_function
import time
import math
import random
import socket
import platform
try:
    import pyfiglet
    __pyfiglet__ = True
except ImportError:
    __pyfiglet__ = False
try:
    import colored
    __colored__ = True
except ImportError:
    __colored__ = False

random.seed()


#
# Gather information
#
dist, ver, flav = platform.linux_distribution(full_distribution_name=True)
kernel   = platform.release()
hostname = socket.gethostname().split(".")[0]


#
# Display
#
print("")
print(
    " ~ Welcome to {0} {1} (Kernel {2}) ~"
        .format(dist, ver, kernel)
        .center(80)
)

def tt_len(text):
    def size(c):
        if c in "qpdbwmWMOQ":
            return 1.3
        elif c in "1frtijlIJ`[];’,. ! ()\"":
            return 0.7
        return 1.0
    return math.ceil(sum(map(size, text)))

if __colored__:
    # Random color based on the current time
    color = int(time.time() % 255)
    color += random.randint(-8, 7)
    color = min(max(color, 1), 230)

    print(colored.fg(color))

if __pyfiglet__:
    # Adapt for to the size of the text
    if tt_len(hostname) < 6:
        font = "big"
    elif tt_len(hostname) < 12:
        font = "standard"
    elif tt_len(hostname) < 20:
        font = "small"
    else:
        font = "digital"

    try:
        figlet = pyfiglet.Figlet(font=font, width=80, justify='center')

    except pyfiglet.FontNotFound:
        # Use default font if a specific font is not found
        figlet = pyfiglet.Figlet(width=80, justify='center')

    print(figlet.renderText(hostname))

else:
    # With no Figlet, write the hostname in the center of the screen
    print("\n%s\n" % hostname.center(80))

if __colored__:
    print(colored.attr("reset"))

exit(0)

# vim: ft=python:ts=4:sw=4