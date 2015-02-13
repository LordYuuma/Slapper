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

from ast import literal_eval as literal
from ConfigParser import ConfigParser, NoSectionError, NoOptionError

# section names used internally
SEC_COMMANDS = "commands"
SEC_COUNT = "count"
SEC_FORMATTING = "formatting"
SEC_OPTIONALS = "optionals"
SEC_REPLACEMENTS = "replacements"
SEC_SETTINGS = "settings"

# key names used internally
KEY_AND = "and"
KEY_COUNT = "count"
KEY_OBJECT = "object"
KEY_RECURSION = "recursion depth"
KEY_TARGET_FORMAT = "target format"
KEY_PRINT_COUNT = "print count"

# defaults
DEF_CMDKEY = "default"
DEF_CMDSLAP = "me slaps {targets} with {object}."

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
            self.set(SEC_REPLACEMENTS, KEY_OBJECT, self.name)
        if not self.has_section(SEC_COUNT):
            self.add_section(SEC_COUNT)
        if not self.has_option(SEC_COUNT, KEY_COUNT):
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

    def __init__(self, _file):
        ConfigParser.__init__(self)
        self._file = _file

    def _define_replacements(self, targets, definitions):
        """
        Formats the replacement dictionary to match the definitions given by the file and the
        user. Subclasses should ALWAYS call this on the first line of their own method, should
        they need to override this.

        Subclass implementations should NOT use targets and definitions themselves. They are
        already handled here.
        Args:
            targets: The targets given by the caller.
            definitions: additional definitions given by the caller.
        Returns:
            the replacement dictionary for the format strings
        Throws:
            None
        """
        replacements = {}
        try:
            replacements.update(self[SEC_REPLACEMENTS].to_dict())
        except (NoSectionError, NoOptionError):
            pass
        if definitions:
            replacements.update(definitions)
        try:
            count = int(self[SEC_COUNT][KEY_COUNT])
        except (NoSectionError, NoOptionError, ValueError):
            count = 0
        replacements.update({"count": count, "count ordinal": ordinal(count),
                             "targets": targets})
        return replacements

    # Takes a list of targets and formats them according to the slapper's formatting options
    # to return a string, that looks like something you can write as part of a sentence.
    def _format_targets(self, targets):
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

    def _format_command(self, cmds, replacements):
        try:
            maxtries = int(self[SEC_SETTINGS][KEY_RECURSION])
        except (NoSectionError, NoOptionError, ValueError):
            maxtries = 8
        tmps = None
        tries = 0
        while not cmds == tmps:
            tmps = cmds
            cmds = tmps.format(**replacements)
            tries += 1
            if tries >= maxtries:
                raise ValueError("Could not format \"{}\".".format(command))
        return cmds

    # formats and executes a slap command
    def _do_slap(self, command, targets="", definitions={}):
        cmds = literal("'" + command.replace("\'", "\\\'") + "'")
        replacements = self._define_replacements(targets, definitions)
        cmds = self._format_command(cmds, replacements)
        for cmd in cmds.split("\n"):
            self.exec_command(cmd)

    def _optionals(self, targets, optionals, definitions={}):
        if not SEC_OPTIONALS in self.sections():
            return
        for optional in optionals:
            try:
                self._do_slap(self[SEC_OPTIONALS][optional], targets, definitions)
            except NoOptionError:
                pass

    def exec_command(self, command):
        """
        How the slapper should execute a given command.

        Args:
            command: an IRC command, that has not been checked for safety whatsoever
        """
        print(command)

    def slap(self, targets, optionals=None, definitions={}):
        """
        Slap all targets.

        Args:
            targets: a list of strings (hopefully target names)
            optionals: a list of optional slap commands
            definitions: a key value map of overridden values by the user
        Returns:
            None
        Raises:
            ValueError: a misconfiguration causes a format string to not
                        be formattable
        """
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
