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

import hexchat
from ast import literal_eval as literal
from ConfigParser import ConfigParser, NoOptionError
from os.path import join

# safe commands used within IRC for saying stuff
CS_SAFE = ["me","say"]

# section names used internally
S_COMMANDS = "commands"
S_SLAPPER = "slapper"

# key names used internally
K_AND = "and"
K_COUNT = "count"
K_OBJECT = "object"
K_TFMT = "target_format"

# preference keys
P_CFGDIR = "slapper_cfg_dir"

# defaults
D_CFGDIR = "slapper"
D_CMDKEY = "default"
D_CMDSLAP = "me slaps \002{target}\002 with {object}."

# file endings
FE_SLAPPER = ".slapper"

# sets plugin preference if not already existing
if not hexchat.get_pluginpref(P_CFGDIR):
    hexchat.set_pluginpref(P_CFGDIR, join(hexchat.get_info("configdir"), D_CFGDIR))

# from this codegolf: http://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
ordinal = lambda n : "{}{}".format(n, "tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])


# utility class for ConfigParser, as it does not yet introduce it's own sections.
# Also it has autoupdate for the file like HexChat Preferences
class SelfUpdatingSection(object):

    def __init__(self, section, parser, _updatefp = None):
        self.section = section
        self.parser = parser
        self._updatefp = _updatefp

    def __getitem__(self, option):
        if self._updatefp: self.parser.read(self._updatefp)
        return self.parser.get(self.section, option)

    def __setitem__(self, option, value):
        self.parser.set(self.section, option, value)
        if self._updatefp:
            with open(self._updatefp, "w") as fd:
                self.parser.write(fd)

    __iter__ = lambda self: ((item[0], item[1]) for item in self.parser.items(self.section))
    __len__ = lambda self: len([item for item in self])
    __repr__ = lambda self: "{" + ", ".join(["\'{}\' : \'{}\'".format(key, value) for key, value in self]) + "}"

class Slapper(ConfigParser):

    __getitem__ = lambda self, section: SelfUpdatingSection(section, self, self.file)
    __iter__ = lambda self: (self[section] for section in self.sections())
    __repr__ = lambda self: "{" + ", ".join(["\'{}\': {}".format(section, repr(self[section])) for section in self.sections()]) + "}"

    def check_sanity(self):
        # This just checks, if every option, that needs to exist, also exists properly.
        # This should only be called by the user, if he thinks, he has REALLY messed up.
        if not self.has_section(S_SLAPPER): self.add_section(S_SLAPPER)
        if not self.has_option(S_SLAPPER, K_OBJECT): self.set(S_SLAPPER, K_OBJECT, self.name)
        if not self.has_option(S_SLAPPER, K_COUNT): self.set(S_SLAPPER, K_COUNT, 0)
        if not self.has_section(S_COMMANDS): self.add_section(S_COMMANDS)
        if not len(self[S_COMMANDS]): self.set(S_COMMANDS, D_CMDKEY, D_CMDSLAP)
        with open(self.file, "w") as fd:
            self.write(fd)

    def __init__(self, name):
        ConfigParser.__init__(self)
        self.name = name
        self.file = join(hexchat.get_pluginpref(P_CFGDIR), self.name + FE_SLAPPER)
        if not self.read(self.file): self.check_sanity()

    def parse_targets(self, targets):
        """
        Takes a list of targets and formats them according to the slapper's formatting options
        to return a string, that looks like something you can write as part of a sentence.
        """
        try:
            t_fmt = self[S_SLAPPER][K_TFMT]
        except NoOptionError:
            t_fmt = "{target}"
        if len(targets) > 1:
            last = targets[-1]
            ts = ", ".join(t_fmt.format(target=t) for t in targets[:-1])
            try:
                a = self[S_SLAPPER][K_AND]
            except NoOptionError:
                a = "and"
            return "{} {} {}".format(ts, a, t_fmt.format(target=last))
        return t_fmt.format(target=targets[0])


    def slap(self, targets):
        # update all the settings from the file.
        # this is important, because a new value may have been set and normally, one does direct
        # file editing for a reason.
        self.read(self.file)
        # This increment's the slapper's use count and also sets it again.
        # Since we use self updating sections, this change is automatically written to the file.
        count = int(self[S_SLAPPER][K_COUNT]) + 1
        self[S_SLAPPER][K_COUNT] = count
        # The following formats the command according to the formatting specs defined, and
        # executes those, that are safely usable.
        for command in sorted(self[S_COMMANDS]):
            cmd = literal("'" + command[1] + "'").format(name = self.name,
                                                         targets = self.parse_targets(targets),
                                                         object = self[S_SLAPPER][K_OBJECT],
                                                         count = count,
                                                         count_ordinal = ordinal(count))
            if(cmd.split(" ")[0].lower() in CS_SAFE):
                hexchat.command(cmd)
