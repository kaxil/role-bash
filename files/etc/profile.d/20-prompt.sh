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
# Custom advanced prompt for BASH
#

# Skip all for noninteractive shells.
[ -z "$PS1" -o ! -t 1 ] && return

_get_git_tag() {
    if ! which git > /dev/null 2>&1 ; then
        echo ""
        exit
    fi

    local branch="$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/' || echo "")"

    if [[ -z "$branch" ]] ; then
        echo ""
        exit
    fi

    local git_diff="$(git diff --numstat --pretty="%H")"
    local git_plus="$(awk 'NF==3 {plus += $1} END {printf("+%d", plus)}' <<< "$git_diff")"
    local git_minus="$(awk 'NF==3 {minus += $2} END {printf("-%d\n", minus)}' <<< "$git_diff")"

    printf "$C_FORE_LIGHT_CYAN$branch$C_FORE_DEFAULT ($C_FORE_LIGHT_GREEN$git_plus $C_FORE_LIGHT_RED$git_minus$C_FORE_DEFAULT)"
}

_set_prompt() {
    local last_command=$?       # Must be the first one here
    local tags=()
    local lines=()
    local oIFS=$IFS; IFS=""

    #
    # Tags
    #

    # Date
    tags+=("$C_FORE_WHITE$(date +"%a %x %X")")

    # Root user
    if [[ $EUID == 0 ]] ; then
        tags+=("${C_FORE_LIGHT_RED}ROOT")
    fi

    # Environment
    local machine_env="$(awk '{print toupper($0)}' <<< $MACHINE_ENV)"
    if [[ "$machine_env" == 'INT' ]] ; then
        tags+=("$C_FORE_LIGHT_YELLOW$machine_env")
    elif [[ "$machine_env" == 'PRD' ]] ; then
        tags+=("$C_FORE_LIGHT_RED$machine_env")
    fi

    # GIT repository
    local git_tag="$(_get_git_tag)"
    if [[ -n "$git_tag" ]] ; then
        tags+=("$git_tag")
    fi

    # Command number
    tags+=("$C_FORE_WHITE\!")

    # Result of last command
    if [[ $last_command != 0 ]] ; then
        tags+=("$C_FORE_LIGHT_RED$last_command")
    fi

    #
    # Lines
    #

    # Building LINE 1
    local line=""
    for tag in "${tags[@]}" ; do
        line="$line$C_FORE_DEFAULT[$tag$C_FORE_DEFAULT]"
    done
    if [[ -n "$line" ]] ; then
        lines+=("$line")
    fi

    # Building LINE 2
    lines+=("\u@\h: $C_FORE_DARK_GRAY\w$C_FORE_DEFAULT")

    # Building LINE 3
    lines+=("\\$ ")

    #
    # Prompt
    #

    export PS1=""
    for ((i = 0; i < ${#lines[@]}; i++)) ; do
        PS1="$PS1\n${lines[$i]}"
    done

    # Emergency prompt, back to the usual one
    #export PS1="\u@\h: \\$ "

    IFS=$oIFS
}

# Prompt in VI Mode
set -o vi

# Custom prompt
export PROMPT_COMMAND="_set_prompt"

# vim: ft=sh:ts=4:sw=4