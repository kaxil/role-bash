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
import re
import os
import math
import json
import time
import fcntl
import random
import socket
import struct
import platform
import datetime
import subprocess

try:
    import psutil
    __psutil__ = True
except ImportError:
    __psutil__ = False

try:
    from colored import fg, attr
    __colored__ = True
except ImportError:
    __colored__ = False

    def fg(dummy):
        return ""

    def attr(dummy):
        return ""


def format_timedelta(seconds, lookup=None, sep=', '):
    """
    Formats a timedelta into a human readable expanded format with a precusion up to microsecond
    """
    if lookup is None:
        loopkup = [
            {'divider': 1,    'format': '{0:.0f} {1}', 'unit': 'us',   'units': 'us',     'value': None},
            {'divider': 1000, 'format': '{0:.0f} {1}', 'unit': 'ms',   'units': 'ms',     'value': 0},
            {'divider': 1000, 'format': '{0:.0f} {1}', 'unit': 'sec',  'units': 'secs',   'value': 0},
            {'divider': 60,   'format': '{0:.0f} {1}', 'unit': 'min',  'units': 'mins',   'value': 0},
            {'divider': 60,   'format': '{0:.0f} {1}', 'unit': 'hour', 'units': 'hours',  'value': 0},
            {'divider': 24,   'format': '{0:.0f} {1}', 'unit': 'day',  'units': 'days',   'value': 0},
            {'divider': 7,    'format': '{0:.0f} {1}', 'unit': 'week', 'units': 'weeks',  'value': 0},
            {'divider': 4.348214, 'format': '{0:.0f} {1}', 'unit': 'month', 'units': 'months', 'value': 0},
            {'divider': 12,   'format': '{0:.0f} {1}', 'unit': 'year',  'units': 'years', 'value': 0},
        ]

    for i, current in enumerate(loopkup):
        if i == 0:
            current.update({'value': round(seconds * 1E+6)})
        else:
            previous = loopkup[i - 1]
            current.update({'value': math.floor(previous['value'] / current['divider'])})
            previous.update({'value': previous['value'] - current['value'] * current['divider']})

    output = ""
    for entry in loopkup:
        if entry['value'] != 0:
            unit   = entry['unit'] if entry['value'] == 1 else entry['units']
            entry  = entry['format'].format(entry['value'], unit)
            output = entry if output == "" else entry + sep + output

    if output == "":
        return "0s"

    return output


def format_filesize(num, suffix='B'):
    """
    See: https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0

    return "%.1f%s%s" % (num, 'Yi', suffix)


def color_level(value, min_value=0.0, max_value=1.0, func=lambda x: x):
    """
    Returns a color based on a value in a range
    """
    global COLOR_SCALE

    if not __colored__:
        return ""

    COLOR_SCALE = [
        fg("white"),
        fg("pale_green_3b"),
        fg("green"),
        fg("green_yellow"),
        fg("light_yellow"),
        fg("orange_1"),
        fg("orange_red_1"),
        fg("light_red"),
        fg("light_red") + attr("blink")
    ]

    max_index = len(COLOR_SCALE) - 1
    color_index = int(round(
        max_index * min(1.0, max(0.0,
            func((value - min_value) / (max_value - min_value))
        ))
    ))

    return COLOR_SCALE[color_index]


def color_loadavg(value):
    """
    Formats the value of loadavg using colors
    """
    if not __colored__ or not __psutil__:
        return "{0:d}%".format(int(math.floor(value * 100)))

    value /= psutil.cpu_count()

    return \
        color_level(value, min_value=0.5, max_value=1.05) +\
        "{0:d}%".format(int(math.floor(value * 100))) +\
        attr("reset")


def file_entry(file_path, regex, default=()):
    """
    Reads an entry from a file using a regular expression and returning a tuple
    """
    with open(file_path, 'r') as f:
        for line in f:
            search = re.search(regex, line, re.IGNORECASE)
            if search:
                return search.groups()

    return default


def add_error_entry(title, description):
    """
    Builds and entry marked as error
    """
    global data_output

    data_output.append({
        'title': title,
        'value': description,
        'color': fg("grey_30")
    })


data_output = []


#
# Date and time
#
try:
    now = datetime.datetime.now()
    time_string = "{0} {1:04d}-{2:02d}-{3:02d} {4:02d}:{5:02d}:{6:02d}.{7:d} {8:+03d}{9}".format(
        now.strftime('%a'),
        now.year, now.month, now.day,
        now.hour, now.minute, now.second, now.microsecond,
        time.timezone if (time.localtime().tm_isdst == 0) else time.altzone / 60 / 60 * -1,
        time.tzname[time.daylight]
    )
    data_output.append({
        'title': 'Time',
        'value': time_string,
        'color': fg("white")
    })

except:
    add_error_entry("Time", "EXCEPTION")


#
# Linux distribution
#
try:
    dist, ver, _ = platform.linux_distribution(full_distribution_name=True)
    data_output.append({
        'title': 'Linux',
        'value': "{0} {1}".format(dist, ver),
        'color': fg("white")
    })

except:
    add_error_entry("Linux", "EXCEPTION")


#
# Provisioner information
#
if os.environ.get('MACHINE_ENV', '') != '':
    try:
        machine_env = os.environ['MACHINE_ENV'].strip().lower()

        color = fg("white")
        if machine_env == 'int':
            color = fg("light_yellow")
        elif machine_env == 'prd':
            color = fg("light_red")

        data_output.append({
            'title': 'Environment',
            'value': os.environ.get('MACHINE_ENV_DESC', machine_env).strip(),
            'color': color
        })

    except:
        add_error_entry("Environment", "EXCEPTION")

if os.environ.get('MACHINE_DC', '') != '':
    try:
        machine_dc = os.environ['MACHINE_DC'].strip().lower()
        data_output.append({
            'title': 'Datacenter',
            'value': os.environ.get('MACHINE_DC_DESC', machine_dc).strip(),
            'color': fg("white")
        })

    except:
        add_error_entry("Datacenter", "EXCEPTION")


#
# Uptime
#
try:
    uptime = file_entry('/proc/uptime', r'^([\d.]+)')[0]
    data_output.append({
        'title': 'Uptime',
        'value': format_timedelta(round(float(uptime))),
        'color': fg("white")
    })

except:
    add_error_entry("Uptime", "EXCEPTION")


#
# CPU Info
#
try:
    cpus = {}
    with open("/proc/cpuinfo") as f:
        for line in f.readlines():
            search = re.search(
                r'^\s*model name\s*:\s*(.*)$',
                line,
                re.IGNORECASE
            )
            if search:
                cpus[search.group(1)] = cpus.get(search.group(1), 0) + 1

    for cpu, count in cpus.iteritems():
        data_output.append({
            'title': "CPU",
            'value': "%s x %s" % (str(count), cpu),
            'color': fg("white")
        })

except:
    add_error_entry("CPU", "EXCEPTION")


#
# Processes
#
if __psutil__:
    try:
        statuses = {}
        for proc in psutil.process_iter():
            try:
                status = proc.status()
                statuses[status] = statuses.get(status, 0) + 1
            except psutil.NoSuchProcess:
                pass

        output = ""
        for status, count in statuses.iteritems():
            if output == "":
                output = "{0} {1}".format(count, status)
            else:
                output = "{0}, {1} {2}".format(output, count, status)

        data_output.append({
            'title': "Processes",
            'value': output,
            'color': fg("white")
        })

    except:
        add_error_entry("Processes", "EXCEPTION")

else:
    add_error_entry("Processes", "MISSING PYTHON PSUTIL")


#
# CPU Load
#
try:
    cpuload = file_entry('/proc/loadavg', r'^([\d.]+) ([\d.]+) ([\d.]+)')
    shortterm = float(cpuload[0])
    midterm   = float(cpuload[1])
    longterm  = float(cpuload[2])

    output = (
        "{0}" + fg("white") + "(1min), "
        "{1}" + fg("white") + "(5min), "
        "{2}" + fg("white") + "(15min)").format(
            color_loadavg(shortterm),
            color_loadavg(midterm),
            color_loadavg(longterm)
        )

    data_output.append({
        'title': 'System Load',
        'value': output,
        'color': fg("white")
    })

except:
    add_error_entry("System Load", "EXCEPTION")


#
# Memory usage
#
try:
    total = file_entry('/proc/meminfo', r'^MemTotal:\s*(\d+)')[0]
    avail = file_entry('/proc/meminfo', r'^MemAvailable:\s*(\d+)')[0]

    total = float(total) * 1024.0
    used = total - float(avail) * 1024.0
    percent_used = used / total

    color = color_level(percent_used, min_value=0.5)
    output = "{0:.1f}% ({1} used of {2})".format(
        percent_used * 100,
        format_filesize(used),
        format_filesize(total)
    )

    data_output.append({
        'title': 'Memory usage',
        'value': output,
        'color': color
    })

except:
    add_error_entry("Memory usage", "EXCEPTION")


#
# Swap usage
#
if __psutil__:
    try:
        swap = psutil.swap_memory()
        total = swap.total
        used = swap.total - swap.free

        if total > 0.0:
            percent_used = float(used) / float(total)
            color = color_level(percent_used, min_value=0.05, max_value=0.5)
            output = "{0:.1f}% ({1} used of {2})".format(
                percent_used * 100,
                format_filesize(used),
                format_filesize(total)
            )

        else:
            color = fg("red")
            output = "Swap not in use."

        data_output.append({
            'title': "Swap usage",
            'value': output,
            'color': color
        })

    except:
        add_error_entry("Disk usage", "EXCEPTION")

else:
    add_error_entry("Disk usage", "MISSING PYTHON PSUTIL")


#
# Disks usage
#
if __psutil__:
    try:
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            percent_used = float(usage.used) / float(usage.total)

            color = color_level(percent_used, min_value=0.6)
            output = "{0:.1f}% on {1} ({2} used of {3})".format(
                percent_used * 100,
                partition.mountpoint,
                format_filesize(usage.used),
                format_filesize(usage.total)
            )

            data_output.append({
                'title': "Disk usage",
                'value': output,
                'color': color
            })

    except:
        add_error_entry("Disk usage", "EXCEPTION")

else:
    add_error_entry("Disk usage", "MISSING PYTHON PSUTIL")


#
# Network info
#

try:
    # Default interface and gateway
    iface = None
    with open("/proc/net/route") as f:
        for line in f.readlines():
            try:
                iface, dest, gateway, flags, _, _, _, _, _, _, _, =  line.strip().split()
                if dest != '00000000' or not int(flags, 16) & 2:
                    continue
                gw = socket.inet_ntoa(struct.pack("<L", int(gateway, 16)))
            except:
                continue

    # IP Address and netmask
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 0)) # Doesn't even have to be reachable
        ip = s.getsockname()[0]
    except:
        pass
    finally:
        s.close()

    if ip and iface:
        data_output.append({
            'title': "Network",
            'value': "{0}({1}) gw {2}".format(ip, iface, gw),
            'color': fg("white")
        })

except:
    add_error_entry("Network", "EXCEPTION")


#
# Users
#
users = {}
if __psutil__:
    try:
        for user in psutil.users():
            users[user.name] = users.get(user.name, 0) + 1

        output = ""
        for user, count in users.iteritems():
            if output == "":
                output = user
            else:
                output = "{0}, {1}".format(user, output)

        data_output.append({
            'title': "Logged users",
            'value': "#{0} ({1})".format(len(users), output),
            'color': fg("white")
        })

    except:
        add_error_entry("Network", "EXCEPTION")

else:
    add_error_entry("Network", "MISSING PYTHON PSUTIL")


#
# Display
#
print("~ System information as {0} ~\n".format(now.isoformat()).center(80))

last_line = {'title': None, 'value': None, 'color': None}
for line in data_output:
    if last_line['title'] == line['title']:
        output = " " * 25
    else:
        output = "   %s" % line['title'].ljust(20, '.') + ": "

    if __colored__ and 'color' in line:
        output += line['color']

    output += line['value']

    if __colored__ and 'color' in line:
        output += attr("reset")

    print(output, end='')
    print("")
    last_line = line

print("")

exit(0)

# vim: ft=python:ts=4:sw=4
