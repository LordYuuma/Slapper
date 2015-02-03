Slapper
=======

The most extensible IRC `/SLAP` you have ever seen.

Installing:
----------
This is a plugin for HexChat. You can get HexChat [from it's homepage](http://hexchat.github.io "Hexchat Homepage").

Slapper consists of two components: the `hc_slapper` python module, which is installed via `setup.py` and the `slapper.py` hexchat plugin, which is best stored in the user's hexchat plugin directory. You can also install it system wide, but we do not recommend that for multiple reasons (autoloading, configuration of said autoloading in multi-user systems, etc. etc.)

Features:
------
* Slapping people in IRC.
* Slapping *multiple* people at once.
* Defining more than one command to be executed to slap someone.
* Usage of long names (with spaces) for both slappers and targets (with escaping!)
* Defining multiple slappers. (Never write more than one plugin)
* Slappers with optional commands.

Usage:
------
### Syntax
`/SLAP [-h] [-c slapper [slapper ...]] [-d key value] [-r] [-s slapper] [-o optional] target [target ...]`
### Positional Arguments
`target` is a target. You can have as many as you want.
### Optional Arguments
`-c|--choice` defines a list of slappers (in your slapper directory) to choose from randomly. Have another option or add `--` before the target list to not confuse the parser ;)

`-d|--definition` can be used to define a key value pair. If key is used in a slapper command, it will be replaced with value.

`-r|--random` same as choice, but with all slappers in your slapper directory.

`-s|--slapper` uses a specific slapper.

`-o|--optional` tells slapper to execute a command, it normally does not use.

For optional commands and definitions, please refer to the slapper configuration.

Slapper Configuration:
------
Slapper configuration files are by default stored in the `slapper` subfolder of your HexChat configuration folder. This can be changed by changing `slapper_cfg_dir` in your `addon_python.conf` to a different directory. The slapper configuration file has the following sections:

* `[formatting]` consists of `target format` to make the names of targets appear bold, italic, whatever... and `and`, which is used when concatenating a list of more than one target to a comma seperated sequence, `and` and the last target.
* `[replacements]` has key value pairs of replacements, which can be used for commands.
* `[count]` has `count`, which is the current usage count.
* `[commands]` are the IRC commands, which are to be executed, when the slapper slaps (a group of) someone(s).
* `[optionals]` are additional commands, which the user may call by adding a certain flag to the command he enters. See usage.



When a command uses a replacement, the key has to be embraced with curly brackets like `{this}`.

Internally used replacements:
-----
The following replacements are made internally. You can not override their values.

* `{targets}`: the targets for slapping. This should be used in your commands, if you want to have the target names actually appear.
* `{count}`: how often the slapper has been used.
* `{count ordinal}`: the same, but this time with english ordinals.
* `{nick}`: your nickname (might be handy sometimes).
