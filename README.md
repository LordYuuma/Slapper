Slapper
=======

The most extensible IRC /slap you have ever seen

Installing:
----------
Run `(sudo) python setup.py install` to install the modules needed for this to work. Then move
`slapper.py` into your hexchat plugin directory.

Usage:
------
To slap someone simply type `/slap <target> [object]`. By default it will then say, that your
slapped target with said object, which is a trout if not given. You can modify the slapper's
configuration file or use the python class `Slapper` from the module `hc_slapper` if you are
more into scripting and stuff.
