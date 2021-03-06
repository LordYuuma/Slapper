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
__module_version__ = "5.3"
__module_description__ = "An extensible '/slap' command for the HexChat IRC client."
__author__ = "LordYuuma"

import hexchat
from slapper import Slapper, NoSectionError, NoOptionError, SEC_COUNT, KEY_USAGES, KEY_TARGETS
from argparse import ArgumentParser, REMAINDER
from inspect import cleandoc
from os import listdir, makedirs
from os.path import basename, dirname, isdir, islink, join, realpath
from random import choice
from shlex import split
from sys import stdout

DEFAULT_SLAPPER = "trout"
DEFAULT_CONF = cleandoc(
    """
    [formatting]
    target format = {target}
    and = and

    [replacements]
    fish = large trout
    fish2 = sligthly smaller trout

    [count]
    targets = 0

    [commands]
    default = me slaps {targets} with a {fish}.

    [optionals]
    one more = me then uses a {fish2} to slap {targets} again.
    print count = me has already slapped {count targets} persons with his {fish}.
    """)

PREFERENCE_CONFDIR = "slapper_cfg_dir"
DEFAULT_CONFDIR = "slapper"


class HexChatSlapper(Slapper):

    def __init__(self, name):
        _file = HexChatSlapper._guess_file(name)
        Slapper.__init__(self, _file)
        self.test = False
        self.hook_after_slap(self._test_reset)

    @staticmethod
    def get_slapperdir():
        """
        Returns the directory used for slapper configuration.
        Args:
            None
        Returns:
            The slapper configuration directory
        Raises:
            None
        """
        d = hexchat.get_pluginpref(PREFERENCE_CONFDIR)
        return d if d else join(hexchat.get_info("configdir"), DEFAULT_CONFDIR)

    @staticmethod
    def _guess_file(name):
        pd = HexChatSlapper.get_slapperdir()
        for f in listdir(pd):
            if basename(join(pd, f)) == name:
                return join(pd, f)
        return join(pd, name)

    def update_replacements(self, replacements, targets, definitions):
        replacements.update({"nick": hexchat.get_info("nick")})

    def exec_command(self, cmd):
        if self.test:
            Slapper.exec_command(self, cmd)
        elif(cmd.split(" ")[0].lower() in ["me", "say"]):
            hexchat.command(cmd)

    def _test_reset(self, targets, optionals, definitions):
        if self.test:
            try:
                self[SEC_COUNT][KEY_USAGES] = str(int(self[SEC_COUNT][KEY_USAGES]) - 1)
            except (KeyError, NoSectionError, NoOptionError):
                pass
            try:
                self[SEC_COUNT][KEY_TARGETS] = str(int(self[SEC_COUNT][KEY_TARGETS]) - len(targets))
            except (KeyError, NoSectionError, NoOptionError):
                pass

def check_defaults():
    confdir = HexChatSlapper.get_slapperdir()
    # Ensure that the directory exists, so we can write our files in it.
    if not isdir(confdir):
        makedirs(confdir)
    # The following is actually better than the default configuration, that is
    # generated by Slapper itself, as it uses the configuration given in the
    # plugin head and therefore helpful comments can be added in the plugin
    # itself, rather than in the module, where just correctness is needed.
    try:
        with open(join(confdir, DEFAULT_SLAPPER)) as fd:
            pass
    except IOError:
        with open(join(confdir, DEFAULT_SLAPPER), "w") as fd:
            fd.write(DEFAULT_CONF)


class SlapParser(ArgumentParser):

    def __init__(self):
        ArgumentParser.__init__(self, prog="/slap")
        self.add_argument('-c', '--choice', type=str, nargs='+', dest="choices",
                          metavar="slapper",
                          help="define choices for random. implies random")
        self.add_argument('-d', '--define', type=str, nargs=2, action="append",
                          dest="definitions", metavar=("key", "value"),
                          help="override a replacement definition of the used slapper")
        self.add_argument("--print-config", nargs='+', metavar='slapper',
                          help="print the configuration of a slapper")
        self.add_argument("-r", "--random", action='store_true', help="use random slapper")
        self.add_argument("-s", "--slapper", type=str, default=DEFAULT_SLAPPER,
                          metavar="slapper", help="specify the slapper to use")
        self.add_argument("-o", "--optional", type=str, action="append", dest="optionals",
                          metavar="optional",
                          help="also execute optional command defined by slapper")
        self.add_argument("-t", "--test", action="store_true",
                          help="show the commands instead of executing them.")
        self.add_argument("targets", nargs=REMAINDER, metavar="target",
                          help="a targeted user")


def get_slappers():
    pd = HexChatSlapper.get_slapperdir()
    return [f for f in listdir(pd) if not isdir(f) and not (islink(join(pd, f)) and dirname(realpath(join(pd, f))) == pd)]


def callback(word, word_eol, userdata):
    parser = SlapParser()
    try:
        if(len(word) < 2):
            parser.print_usage()
            print("Error: You need at least one target.")
            raise SystemExit

        slap = parser.parse_args(split(word_eol[1]))

        if slap.print_config:
            for config in slap.print_config:
                with HexChatSlapper(config) as slapper:
                    print("Configuration for {} ({}):".format(config, slapper._file))
                    slapper.write(stdout)
            return hexchat.EAT_ALL

        if slap.random or slap.choices:
            if not slap.choices:
                slap.choices = get_slappers()
            slap.slapper = choice(slap.choices)

        with HexChatSlapper(slap.slapper) as slapper:
            slapper.test = slap.test
            slapper.slap(slap.targets, optionals=slap.optionals,
                         definitions=slap.definitions)
    except IndexError:
        parser.print_help()
        if not slap.print_config and not slap.targets:
            print("Error: You need at least one target.")
    except SystemExit:
        # ArgumentParser raises SystemExit when called with -h/--help
        # this here is just so that the user can actually see the help
        pass
    return hexchat.EAT_ALL

def unload(userdata):
    print("{module} {version} unloaded.".format(module=__module_name__,
                                                version=__module_version__))

try:
    check_defaults()
    hexchat.hook_command("SLAP", callback,
                         help=SlapParser().format_help())
    print("{module} {version} by {author} loaded.".format(module=__module_name__,
                                                          version=__module_version__,
                                                          author=__author__))
    hexchat.hook_unload(unload)
except Exception:
    print("Slapper could not be loaded.")
