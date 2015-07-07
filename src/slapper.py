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

from sys import version_info as py

from ast import literal_eval as literal

if py.major == 2:
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError
elif py.major == 3:
    from configparser import ConfigParser, NoSectionError, NoOptionError
else:
    raise InputError("Python version could not be detected.")

# section names used internally
SEC_COMMANDS = "commands"
SEC_COUNT = "count"
SEC_FORMATTING = "formatting"
SEC_OPTIONALS = "optionals"
SEC_REPLACEMENTS = "replacements"
SEC_SETTINGS = "settings"

# key names used internally
KEY_AND = "and"
KEY_OBJECT = "object"
KEY_RECURSION = "recursion depth"
KEY_TARGETS = "targets"
KEY_TARGET_FORMAT = "target format"
KEY_USAGES = "usages"

# defaults
DEF_CMDKEY = "default"
DEF_CMDSLAP = "me slaps {targets} with {object}."

if py.major == 2:
##### PYTHON 2 #####
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
##### PYTHON 2 #####

class Slapper(ConfigParser):

    if py.major == 2:
    ##### PYTHON 2 #####
        __getitem__ = lambda self, section: ConfigParserSection(self, section)
        __iter__ = lambda self: (self[section] for section in self.sections())
        __repr__ = lambda self: "{" + ", ".join(["\'{}\': {}".format(section, repr(self[section])) for section in self.sections()]) + "}"
    ##### PYTHON 2 #####

    def _check_sanity(self):
        # This just checks, if every option, that needs to exist, also exists properly.
        # This should only be called by the user, if he thinks, he has REALLY
        # messed up.
        if not self.has_section(SEC_REPLACEMENTS):
            self.add_section(SEC_REPLACEMENTS)
        if not self.has_option(SEC_REPLACEMENTS, KEY_OBJECT):
            self.set(SEC_REPLACEMENTS, KEY_OBJECT, self.name)
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
        replacements = {}
        if self.has_section(SEC_REPLACEMENTS):
            if py.major == 2:
                replacements.update(self[SEC_REPLACEMENTS].to_dict())
            if py.major == 3:
                replacements.update({key: self[SEC_REPLACEMENTS][key]
                                     for key in self[SEC_REPLACEMENTS]})
        if definitions:
            replacements.update(definitions)

        if self.has_option(SEC_COUNT, KEY_USAGES):
            count_usages = int(self[SEC_COUNT][KEY_USAGES])
        else:
            count_usages = 0
        if self.has_option(SEC_COUNT, KEY_TARGETS):
            count_targets = int(self[SEC_COUNT][KEY_TARGETS])
        else:
            count_targets = 0

        replacements.update({"count usages": count_usages,
                             "count targets": count_targets, "targets": targets})
        self.update_replacements(replacements, targets, definitions)
        return replacements

    # Takes a list of targets and formats them according to the slapper's formatting options
    # to return a string, that looks like something you can write as part of a sentence.
    def _format_targets(self, targets):
        if self.has_option(SEC_FORMATTING, KEY_TARGET_FORMAT):
            t_fmt = self[SEC_FORMATTING][KEY_TARGET_FORMAT]
        else:
            t_fmt = "{target}"
        if self.has_option(SEC_COUNT, KEY_TARGETS):
            self[SEC_COUNT][KEY_TARGETS] = str(int(self[SEC_COUNT][KEY_TARGETS]) + len(targets))
        if len(targets) > 1:
            last = targets[-1]
            ts = ", ".join(t_fmt.format(target=t) for t in targets[:-1])

            if self.has_option(SEC_FORMATTING, KEY_AND):
                a = self[SEC_FORMATTING][KEY_AND]
            else:
                a = "and"
            return "{} {} {}".format(ts, a, t_fmt.format(target=last))
        return t_fmt.format(target=targets[0])

    def _format_command(self, cmds, replacements):
        if self.has_option(SEC_SETTINGS, KEY_RECURSION):
            maxtries = int(self[SEC_SETTINGS][KEY_RECURSION])
        else:
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
        if self.has_option(SEC_COUNT, KEY_USAGES):
            self[SEC_COUNT][KEY_USAGES] = str(int(self[SEC_COUNT][KEY_USAGES]) + 1)
        ts = self._format_targets(targets)
        if py.major == 2:
        ##### PYTHON 2 #####
            for key, command in sorted(self[SEC_COMMANDS]):
                self._do_slap(command, ts, definitions)
        ##### PYTHON 2 #####
        if py.major == 3:
        ##### PYTHON 3 #####
            for key in sorted(self[SEC_COMMANDS]):
                self._do_slap(self[SEC_COMMANDS][key], ts, definitions)
        if optionals:
            self._optionals(ts, optionals, definitions)

    def update_replacements(self, replacements, targets, definitions):
        """
        Use this call to update the replacements of the slapper according to the replacements
        you are about to make. Note that targets and all definitions in definitions have
        already been added.

        Args:
            replacements: the replacements to update
            targets: the targets of the slap
            definitions: the definitions, which where already added
        Returns:
            None
        Raises:
            None
        """
        pass
