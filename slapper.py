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
from ast import literal_eval as literal
from os.path import abspath, basename, dirname, splitext

CONF_PREFIX = "Slapper"
CONF_KEY_COMMAND = "command"
CONF_KEY_COUNT = "count"
CONF_KEY_OBJECT = "object"

DEFAULT_SLAPPER = "trout"
DEFAULT_OBJECT = "a large trout"

def strip_prefixes(string, *prefixes):
    string = parts_to_prefkey(string)
    prefix = parts_to_prefkey(*prefixes)
    if not string.find(prefix): string = string.replace(prefix, "", 1)
    return parts_to_prefkey(string.replace("_", " "))

parts_to_prefkey = lambda *parts, **format_args : " ".join(parts).format(**format_args).replace("'", "").replace("\"","").lower().strip().replace(" ", "_")

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
        self.prefkeys = parts_to_prefkey(*args)

    __getitem__ = lambda self, key : hexchat.get_pluginpref(parts_to_prefkey(self.prefkeys, "{key}", key = key))
    __setitem__ = lambda self, key, value : hexchat.set_pluginpref(parts_to_prefkey(self.prefkeys, "{key}", key = key), value)
    __delitem__ = lambda self, key : hexchat.del_pluginpref(parts_to_prefkey(self.prefkeys, "{key}", key = key))
    __iter__ = lambda self : ((strip_prefixes(pref, self.prefkeys), hexchat.get_pluginpref(pref)) for pref in hexchat.list_pluginpref() if parts_to_prefkey(self.prefkeys) in pref)
    __repr__ = lambda self : "{" + ", ".join(["\'" + key + "\' : \'" + pref + "\'" for key, pref in self]) + "}" # reconstructed dict's repr, so that formatting is the same as in the hexchat output.
    __len__ = lambda self : len([obj for obj in self])

class Slapper(object):

    count = property(lambda self : hexchat.get_pluginpref(parts_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_COUNT)),
                     lambda self, value : hexchat.set_pluginpref(parts_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_COUNT), value),
                     lambda self : hexchat.del_pluginpref(parts_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_COUNT)))

    slapobject = property(lambda self : hexchat.get_pluginpref(parts_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_OBJECT)),
                          lambda self, value : hexchat.set_pluginpref(parts_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_OBJECT), value),
                          lambda self : hexchat.del_pluginpref(parts_to_prefkey(CONF_PREFIX, self.name, CONF_KEY_OBJECT)))

    def __init__(self, name):
        self.name = name
        if not self.slapobject:
            self.slapobject = self.name
        self.commands = HexchatPrefList(CONF_PREFIX, self.name, CONF_KEY_COMMAND)
        if len(self.commands) == 0: self.commands["default"] = "me slaps \002{target}\002 with {slapobject}."

    # a few things you should know:
    # 1st: commands are python format strings, that are interpreted as hexchat commands.
    # 2nd: "py exec" followed by any python statement IS a valid hexchat command if you load this plugin.
    # 3rd: this CAN be used to nuke your system.
    # 4th: I do not intend to check your input, as any limitation would also mean not letting you do the cool stuff :>
    # 5th: Don't let anybody mess up with your config files.
    # 6th: This is not a security issue as anyone, who has access to this plugin's variables already has access to much more important stuff on your machine
    def slap(self, target):
        self.count = (self.count if self.count != None else 0) + 1
        for key, command in self.commands:
            hexchat.command(literal("'" + command + "'").format(name = self.name, target = target, slapobject = self.slapobject, count = self.count, count_ordinal = ordinal(self.count)))

default_slapper = Slapper(DEFAULT_SLAPPER)
if default_slapper.slapobject == DEFAULT_SLAPPER:
    default_slapper.slapobject = DEFAULT_OBJECT
hexchat.hook_command("SLAP", callback, help = "/slap <nick> [object] slaps nick with object.")

# this imports the Slapper into the hexchat python interface, so that you can interact with it.
hexchat.command("py exec if not \"{path}\" in __import__('sys').path: __import__('sys').path.append(\"{path}\")".format(path=dirname(abspath(__file__))))
hexchat.command("py exec {cls} =  __import__('{module}').{cls}".format(module=splitext(basename(__file__))[0], cls = "Slapper"))
hexchat.hook_unload(lambda userdata : hexchat.command("py exec del {cls}".format(cls = "Slapper")))

print("{module} {version} by {author} loaded.".format(module = __module_name__, version = __module_version__, author = __author__))
