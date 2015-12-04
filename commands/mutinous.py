"""
Mutinous Commands are generally experimental.
"""

from evennia import Command


class CmdSwear(Command):
    """
    A swearing command.

    Usage:
        swear [at] [<someone>]
        curse [at] [<someone>]

    Swears at a person in your area or at the room in general.

    """

    key = "swear"
    aliases = ["swear at", "curse", "curse at"]
    locks = "cmd:all()"
    help_category = "Mutinous Commands"

    def parse(self):
        "Very trivial parser"
        self.target = self.args.strip()

    def func(self):
        "This actually does things"
        caller = self.caller
        if not self.target or self.target == "here":
            # called without args or maybe "swear at here"
            string = "%s swears like a sailor." % caller.name
            caller.location.msg_contents(string, exclude=caller)
            # that displays the effect to the room but not the swearer
            caller.msg("You swear like a sailor at the world in general.")
            # and this is the swearers feedback
        else:
            target = caller.search(self.target)
            # hmm does this check if target exists, in the room?
            if not target:
                # caller.search handles error messages. (nice)
                return
            string = "%s curses like a sailor at you!" % caller.name
            target.msg(string)
            string = "You swear like a sailor at %s." % target.name
            caller.msg(string)
            string = "%s curses like a sailor at %s." % (
                caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller, target])
# last line
