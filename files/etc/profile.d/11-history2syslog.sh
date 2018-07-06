#!/bin/bash
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
# Bash History to Syslog
#

# Skip all for noninteractive shells.
[ -z "$PS1" -o ! -t 1 ] && return

function trim
{
    echo "$(echo "$*" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
}

function _history2syslog
{
    cmd=$(history 1 | awk '{ print substr($0, 26) }')

    if [[ "$cmd" != "$old_command" ]] ; then       # Don't log duplicates
        logger -p "local7.notice" -t "shell[$$]" -- "Host: $REMOTE_HOST, User: $LOGNAME, PWD: $(pwd), CMD: $(trim "$cmd")"
    fi

    old_command=$cmd
}

# User remote host
REMOTE_HOST=$(who am i | sed -nre 's/^.*\(([^)]+)\).*/\1/p')

trap _history2syslog DEBUG || EXIT

# vim: ft=sh:ts=4:sw=4