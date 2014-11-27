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
__module_version__ = "3.1"
__module_description__ = "An extensible '/slap' command for the HexChat IRC client."
__author__ = "LordYuuma"

import hexchat
from hc_slapper import Slapper, P_CFGDIR, FE_SLAPPER
from argparse import ArgumentParser, REMAINDER
from inspect import cleandoc
from os import makedirs
from os.path import isdir, join
from shlex import split

DEFAULT_SLAPPER = "trout"
DEFAULT_CONF = cleandoc(
"""
[slapper]
object = a large trout
count = 0

[commands]
default = me slaps {targets} with {object}.
""")

def check_defaults():
    confdir = hexchat.get_pluginpref(P_CFGDIR)
    if not confdir: raise Exception("Configuration not available")
    if not isdir(confdir): makedirs(confdir)
    try:
        with open(join(confdir, DEFAULT_SLAPPER + FE_SLAPPER)) as fd:
            pass
    except IOError:
         with open(join(confdir, DEFAULT_SLAPPER + FE_SLAPPER), "w") as fd:
            fd.write(DEFAULT_CONF)

class SlapParser(ArgumentParser):

    def __init__(self):
        ArgumentParser.__init__(self, prog="/slap")
        self.add_argument("-s", "--slapper", type=str, default=DEFAULT_SLAPPER,
                          help="specify the slapper to use")
        self.add_argument("targets", nargs="+", metavar="target",
                          help="a targeted user")

def callback(word, word_eol, userdata):
    if len(word) < 2:
        print("You slapped no one.")
    else:
        try:
            slap = SlapParser().parse_args(split(word_eol[1]))
            Slapper(slap.slapper).slap(slap.targets)
        except SystemExit:
            pass # For help printing etc.
    return hexchat.EAT_ALL

try:
    check_defaults()
    hexchat.hook_command("SLAP", callback, help = "usage: /slap [-h] [-s SLAPPER] target [target ...]\nuse /slap --help for a full help")
    print("{module} {version} by {author} loaded.".format(module = __module_name__, version = __module_version__, author = __author__))
except Exception:
    print("Slapper could not be loaded.")
