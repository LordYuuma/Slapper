Slapper
=======

The most extensible IRC /slap you have ever seen

Installing:
----------
This is a plugin for HexChat. You can get HexChat [from it's homepage](http://hexchat.github.io "Hexchat Homepage").

Run `(sudo) python setup.py install` to install the modules needed for this to work. Then move
`slapper.py` into your hexchat plugin directory.

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
To slap one (or multiple) target(s) use `/slap <target(s)>`. All of your targets will then be
slapped (one slap statement for everyone to prevent spamming). To specify a slapper, that is
not a trout, use `/slap -s <slapper> <target(s)>`. Slapper and targets are seperated by spaces,
but you can quote them or escape the spaces to specify a longer name. Whenever you feel like
needing help use `/slap --help`.

Slapper Configuration:
------
The slapper configuration file has the following sections:

* `[formatting]` consists of `target_format` to make the names of targets appear bold, italic, whatever... and `and`, which is used when concatenating a list of more than one target to a comma seperated sequence, `and` and the last target.
* `[replacements]` has key value pairs of replacements, which can be used for commands. Note, that using `target`, `count` and `count_ordinal` may lead to unwanted behaviour, since they are already used internally.
* `[count]` has `count`, which is the current usage count and possibly commands which are used to show said count.
* `[commands]` are the IRC commands, which are to be executed, when the slapper slaps (a group of) someone(s).
* `[optionals]` are additional commands, which the user may call by adding a certain flag to the command he enters.



When a command uses a replacement, the key has to be embraced with curly brackets like `{this}`.
