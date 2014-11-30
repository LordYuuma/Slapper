Slapper
=======

The most extensible IRC /slap you have ever seen

Installing:
----------
Run `(sudo) python setup.py install` to install the modules needed for this to work. Then move
`slapper.py` into your hexchat plugin directory.

Features:
------
* Slapping people in IRC.
* Slapping *multiple* people at once.
* Defining more than one command to be executed to slap someone.
* Usage of long names (with spaces) for both slappers and targets (with escaping!)
* Defining multiple slappers. (Never write more than one plugin)

Usage:
------
To slap one (or multiple) target(s) use `/slap <target(s)>`. All of your targets will then be
slapped (one slap statement for everyone to prevent spamming). To specify a slapper, that is
not a trout, use `/slap -s <slapper> <target(s)>`. Slapper and targets are seperated by spaces,
but you can quote them or escape the spaces to specify a longer name. Whenever you feel like
needing help use `/slap --help`.

Slapper Configuration:
------
The following keys are used and configurable for each Slapper:
* `object`: the name of the object used to slap someone with
* `count`: the usage count. (This is mostly used for the internal incrementation, but we let you have fun with it)
* `target_format`: use HexChat codes for formatting the names of your targets.
* `and`: for localization when targetting multiple users. For example *Foo and Bar* sounds perfectly fine in English, but for the use in a german sentence it should be reworded *Foo und Bar*.

The commands in the commands section use Python format strings, where the following replacments
are made:
* `{object}` is replaced with the object
* `{targets}` is replaced with the targets you slapped
* `{count}` is replaced with the usage count of your slapper
* `{count_ordinal}` is replaced with the (english) ordinal of your usage count
