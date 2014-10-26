Slapper
=======

The most extensible IRC /slap you have ever seen

Installing:
----------
Put this into your hexchat/addons directory and then load it. Make sure you have the python
interface for hexchat installed.

Usage:
------
    To slap someone simply type /slap <target> [object]. By default you will then hit your
    target with a trout. Use the python class for defining more objects to hit someone with.

    Slapper("foo") will create a new Slapper called "foo". foo = Slapper("foo") will do the
    same but assign this to the variable foo.

    Now that you have foo, you can set foo.slapobject = "bar". If you then slap someone with
    foo it will actually slap this person with bar.

    If you don't like the wording of your slapcommand, you can change that with
    foo.commands[i], where i is any key you like (for now, we use numeric keys by default,
    but it can be any key you like).
    The commands are python format strings for which the following replacements are made:
        {target} = the target
        {slapobject} = the object
        {count} = the current usage count of this object
        {count_ordinal} = the current usage count in english ordinals

    You can also modify the count manually with foo.count.

TODO:
-----
    Remove hardcoded command[0]
    customizable count offset and stepsize.
