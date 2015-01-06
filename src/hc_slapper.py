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
from ConfigParser import ConfigParser, NoSectionError, NoOptionError
from os import listdir
from os.path import basename, join

# safe commands used within IRC for saying stuff
CS_SAFE = ["me", "say"]

# section names used internally
SEC_COMMANDS = "commands"
SEC_COUNT = "count"
SEC_FORMATTING = "formatting"
SEC_OPTIONALS = "optionals"
SEC_REPLACEMENTS = "replacements"

# key names used internally
KEY_AND = "and"
KEY_COUNT = "count"
KEY_OBJECT = "object"
KEY_TARGET_FORMAT = "target_format"
KEY_PRINT_COUNT = "print_count"

# preference keys
PREF_CFGDIR = "slapper_cfg_dir"

# defaults
DEF_CFGDIR = "slapper"
DEF_CMDKEY = "default"
DEF_CMDSLAP = "me slaps {targets} with {object}."

# sets plugin preference if not already existing
if not hexchat.get_pluginpref(PREF_CFGDIR):
    hexchat.set_pluginpref(PREF_CFGDIR, join(hexchat.get_info("configdir"), DEF_CFGDIR))

# from this codegolf:
# http://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
ordinal = lambda n: "{}{}".format(n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


# utility class for ConfigParser, as it does not yet introduce it's own sections.
# Also it has autoupdate for the file like HexChat Preferences
class ConfigParserSection(object):

    def __init__(self, parser, section):
        self.parser = parser
        self.section = section

    def __getitem__(self, option):
        return self.parser.get(self.section, option)

    def __setitem__(self, option, value):
        self.parser.set(self.section, option, value)

    __iter__ = lambda self: ((item[0], item[1]) for item in self.parser.items(self.section))
    __len__ = lambda self: len([item for item in self])
    __repr__ = lambda self: "{" + ", ".join(["\'{}\' : \'{}\'".format(key, value) for key, value in self]) + "}"

    to_dict = lambda self: {item[0]: item[1] for item in self.parser.items(self.section)}


class Slapper(ConfigParser):

    __getitem__ = lambda self, section: ConfigParserSection(self, section)
    __iter__ = lambda self: (self[section] for section in self.sections())
    __repr__ = lambda self: "{" + ", ".join(["\'{}\': {}".format(section, repr(self[section])) for section in self.sections()]) + "}"

    def _check_sanity(self):
        # This just checks, if every option, that needs to exist, also exists properly.
        # This should only be called by the user, if he thinks, he has REALLY
        # messed up.
        if not self.has_section(SEC_REPLACEMENTS):
            self.add_section(SEC_REPLACEMENTS)
        if not self.has_option(SEC_REPLACEMENTS, KEY_OBJECT):
            self.set(SEC_SLAPPER, KEY_OBJECT, self.name)
        if not self.has_section(SEC_USAGE):
            self.add_section(SEC_USAGE)
        if not self.has_option(SEC_USAGE, KEY_COUNT):
            self.set(SEC_SLAPPER, KEY_COUNT, 0)
        if not self.has_section(SEC_COMMANDS):
            self.add_section(SEC_COMMANDS)
        if not len(self[SEC_COMMANDS]):
            self.set(SEC_COMMANDS, DEF_CMDKEY, DEF_CMDSLAP)

    def __enter__(self):
        if not self.read(self._file):
            self._check_sanity()
        return self

    def __exit__(self, type, value, traceback):
        with open(self._file, "w") as fd:
            self.write(fd)

    def __init__(self, name):
        ConfigParser.__init__(self)
        self.name = name
        self._file = self._guess_file()

    def _guess_file(self):
        pd = hexchat.get_pluginpref(PREF_CFGDIR)
        for f in listdir(pd):
            if basename(join(pd,f)) == self.name:
                return join(pd,f)
        return join(pd, self.name)

    def _format_targets(self, targets):
        """
        Takes a list of targets and formats them according to the slapper's formatting options
        to return a string, that looks like something you can write as part of a sentence.
        """
        try:
            t_fmt = self[SEC_FORMATTING][KEY_TARGET_FORMAT]
        except (NoSectionError, NoOptionError):
            t_fmt = "{target}"
        if len(targets) > 1:
            last = targets[-1]
            ts = ", ".join(t_fmt.format(target=t) for t in targets[:-1])
            try:
                a = self[SEC_FORMATTING][KEY_AND]
            except (NoSectionError, NoOptionError):
                a = "and"
            return "{} {} {}".format(ts, a, t_fmt.format(target=last))
        return t_fmt.format(target=targets[0])

    # formats and executes a slap command
    def _do_slap(self, command, targets="", definitions={}):
        try:
            count = int(self[SEC_COUNT][KEY_COUNT])
        except (NoSectionError, NoOptionError, ValueError):
            count = 0
        cmds = literal("'" + command + "'")
        replacements = self[SEC_REPLACEMENTS].to_dict().copy()
        replacements.update(definitions)
        cmds = cmds.format(count=count, count_ordinal=ordinal(count), targets=targets,
                           **replacements)
        for cmd in cmds.split("\n"):
            if(cmd.split(" ")[0].lower() in CS_SAFE):
                hexchat.command(cmd)

    def _print_count(self):
        if not SEC_COUNT in self.sections():
            return
        for key, command in sorted(self[SEC_COUNT]):
            if not key == KEY_COUNT:
                try:
                    self._do_slap(command)
                except NoOptionError:
                    pass

    def _optionals(self, targets, optionals, definitions={}):
        if not SEC_OPTIONALS in self.sections():
            return
        for optional in optionals:
            try:
                self._do_slap(self[SEC_OPTIONALS][optional], targets, definitions)
            except NoOptionError:
                pass

    def slap(self, targets, optionals=None, definitions={}):
        try:
            count = int(self[SEC_COUNT][KEY_COUNT]) + 1
            self[SEC_COUNT][KEY_COUNT] = str(count)
        except (NoSectionError, NoOptionError):
            pass
        ts = self._format_targets(targets)
        for key, command in sorted(self[SEC_COMMANDS]):
            self._do_slap(command, ts, definitions)
        if optionals:
            self._optionals(ts, optionals, definitions)
        self._print_count()
