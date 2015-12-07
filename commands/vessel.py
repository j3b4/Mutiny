# Commands for Ships and Boats etc.

from evennia import Command, CmdSet

"""
TODO: Commands for navigation.  Set Course. 

"""

class CmdBoard(Command):
    """
    boarding a vessel

    Usage:
        board <vessel>

    This command is available to players in the same location
    as the vessel and allows them to embark.
    """

    key = "board"
    aliases = ["embark", "board ship", "come aboard", ]
    help_category = "Mutinous Commands"
    locks = "cmd:not cmdinside()"

    # adding a parser? or something to allow multiple vessels in one room.

    def func(self):
        vessel = self.obj
        self.caller.msg("You board the vessel")
        self.caller.move_to(vessel)


class CmdDebark(Command):
    """
    disembark or deboard from a vessel. Come ashore.

    Usage:
        debark

    This command is available when you are on a vessel. It will move you to the
    room presently containing the vessel.

    TODO:  debark from one ship to another or create a "transfer" command.
    """

    key = "debark"
    aliases = ["disembark", "deboard", "land", "come ashore", ]
    help_category = "Mutinous Commands"
    locks = "cmd:cmdinside()"

    def func(self):
        vessel = self.obj
        parent = vessel.location
        self.caller.move_to(parent)


class CmdSetVessel(CmdSet):
    "Add these commands to the vessel when it is created."

    def at_cmdset_creation(self):
        self.add(CmdBoard())
        self.add(CmdDebark())

# last line
