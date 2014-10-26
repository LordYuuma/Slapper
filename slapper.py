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
__module_version__ = "2.0"
__module_description__ = "An extensible '/slap' command for the HexChat IRC client."
__author__ = "LordYuuma"

import hexchat
from ast import literal_eval as literal
from os.path import abspath, basename, dirname, splitext

CONF_PREFIX = "Slapper"
CONF_KEY_COMMAND = "command"
CONF_KEY_COUNT = "count"
CONF_KEY_OBJECT = "object"

DEFAULT_SLAPPER = "trout"
DEFAULT_OBJECT = "a large trout"

vars_to_prefkey = lambda *args, **kwargs : " ".join(args).format(**kwargs).replace("'", "").replace("\"","").lower().strip().replace(" ", "_")

# from this codegolf: http://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
ordinal = lambda n : "{}{}".format(n, "tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

def callback(word, word_eol, userdata):
    if len(word) < 2:
        print("You slapped no one.")
    else:
        target = word[1]
        slapper = word_eol[2] if len(word) > 2 else DEFAULT_SLAPPER
        Slapper(slapper).slap(target)
    return hexchat.EAT_ALL

# this is a utility class, that acts like a list towards python and calls the hexchat interface upon usage
class HexchatPrefList(object):

    def __init__(self, *args):
        self.prefkeys = vars_to_prefkey(*args)

    __getitem__ = lambda self, key : hexchat.get_pluginpref(vars_to_prefkey(self.prefkeys, "{key}", key = key))
    __setitem__ = lambda self, key, value : hexchat.set_pluginpref(vars_to_prefkey(self.prefkeys, "{key}", key = key), value)
    __delitem__ = lambda self, key : hexchat.del_pluginpref(vars_to_prefkey(self.prefkeys, "{key}", key = key))
    __iter__ = lambda self : (hexchat.get_pluginpref(cmd) for cmd in hexchat.list_pluginpref() if vars_to_prefkey(self.prefkeys) in cmd)
    __repr__ = lambda self : "[" + ", ".join(["\"" + pref + "\"" for pref in self]) + "]" # reconstructed list's repr, so that formatting is the same as in hexchat.

class Slapper(object):

    count = property(lambda self : hexchat.get_pluginpref(vars_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_COUNT)),
                     lambda self, value : hexchat.set_pluginpref(vars_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_COUNT), value),
                     lambda self : hexchat.del_pluginpref(vars_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_COUNT)))

    slapobject = property(lambda self : hexchat.get_pluginpref(vars_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_OBJECT)),
                          lambda self, value : hexchat.set_pluginpref(vars_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_OBJECT), value),
                          lambda self : hexchat.del_pluginpref(vars_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_OBJECT)))

    def __init__(self, name):
        self.name = name
        if not self.slapobject:
            self.slapobject = self.name
        self.commands = HexchatPrefList(CONF_PREFIX, self.name, CONF_KEY_COMMAND)
        if not self.commands[0]:
            self.commands[0] = "me slaps \002{target}\002 with {slapobject}."

    def slap(self, target):
        self.count = self.count + 1 if self.count else 1
        for command in self.commands:
            hexchat.command(literal("'" + command + "'").format(target = target, slapobject = self.slapobject, count = self.count, count_ordinal = ordinal(self.count)))

default_slapper = Slapper(DEFAULT_SLAPPER)
if default_slapper.slapobject == DEFAULT_SLAPPER:
    default_slapper.slapobject = DEFAULT_OBJECT

hexchat.hook_command("SLAP", callback, help = "/slap <nick> [object] slaps nick with object.")

# this imports the Slapper into the hexchat python interface, so that you can interact with it.
hexchat.command("py exec if not \"{path}\" in __import__('sys').path: __import__('sys').path.append(\"{path}\")".format(path=dirname(abspath(__file__))))
hexchat.command("py exec {cls} =  __import__('{module}').{cls}".format(module=splitext(basename(__file__))[0], cls = "Slapper"))
hexchat.hook_unload(lambda userdata : hexchat.command("py exec del {cls}".format(cls = "Slapper")))

print("{module} {version} by {author} loaded.".format(module = __module_name__, version = __module_version__, author = __author__))
