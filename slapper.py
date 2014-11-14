# Slapper - the most extensible IRC /slap you have ever seen
# Copyright (C) 2014 Lord Yuuma von Combobreaker

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__module_name__ = "Slapper"
__module_version__ = "2.2"
__module_description__ = "An extensible '/slap' command for the HexChat IRC client."
__author__ = "LordYuuma"

import hexchat
from inspect import cleandoc
from re import match
from hc_slapper import Slapper

DEFAULT_SLAPPER = "trout"
DEFAULT_CONF = cleandoc(
"""
[slapper]
object = a large trout
count = 5

[commands]
default = me slaps \002{target}\002 with {object}.
""")

def callback(word, word_eol, userdata):
    if len(word) < 2:
        print("You slapped no one.")
    else:
        try:
            target = match("\"(\w+)\"", word_eol[1]).groups
            offset = 1 + len(target.split())
        except AttributeError:
            target = word[1]
            offset = 2
        slapper = word_eol[offset] if len(word) > offset else DEFAULT_SLAPPER
        Slapper(slapper).slap(target)
    return hexchat.EAT_ALL
