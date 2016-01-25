# Commands for Ships and Boats etc.

from evennia import Command, CmdSet
from evennia import default_cmds
from commands.searoom import CmdSetPosition

# from evennia import default_cmds

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
        self.caller.move_to(vessel)
        self.caller.msg("You board the %s" % vessel)


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


class CmdLookout(default_cmds.CmdLook):
    # Trying to overload the look command so that it behaves
    # differently when called by a character on a vessel.
    """
    Look around yourself while on board a vessel.

    Usage: look

    This command is available when you are on a vessel. It will
    describe the boat or boat-section you are in as well as the area
    the boat is presently passing through.
    """
    # locks = "cmd:cmdinside()"
    help_category = "Mutinous Commands"
    # TODO: add a return_outside_view hook to the vessel object.

    def func(self):
        caller = self.caller
        vessel = self.obj
        outside = vessel.location
        " First copy default look function"
        if not self.args:
            target = caller.location
            if not target:
                self.caller.msg("No location to look at!")
                return
            if caller.location == outside:
                self.msg(caller.at_look(target))
                return
            # no args means this is where the vessel look should sit.
            outboard_view = (vessel.at_look(outside))
            inboard_view = self.caller.at_look(target)
            caller.msg("You're on the %s" % vessel.key)
            # caller.msg("Outside you see:")
            caller.msg(outboard_view)
            caller.msg("Inside you see:\n")
            caller.msg(inboard_view)
        else:
            # if there are arguemnts then do a standard look on them
            target = self.caller.search(self.args)
            if not target:
                return
            self.msg(caller.at_look(target))


class CmdSteer(Command):
    """
    Steer the boat in a direction.
    In a coastal room, this will make the vessel move through any available
    exit which matches the direction named.

    Usage: steer <direction>
    """

    key = "steer"
    aliases = ["pilot", "pi", ]
    help_category = "Mutinous Commands"
    # locks = "cmd:cmdinside()"
    # arg_regex = r"\s|$"

    def parse(self):
        "Get the direction to use as a command for the ship"
        # direction = None
        self.direction = self.args

    def func(self):
        """
        Steering the vessel
        """
        vessel = self.obj
        outside = vessel.location
        # exits = outside.exits
        if self.caller.location == outside:
            self.msg("You need to be on board to %s" % self.key)
            return
        if not self.direction:
            self.msg("Usage: steer <direction>")
            return
        else:
            # self.msg("You try to move %r." % self.direction)
            # self.msg("Available exits include: %s." % exits)
            vessel.execute_cmd(self.direction, sessid=self.caller.sessid)


class CmdSetVessel(CmdSet):
    "Add these commands to the vessel when it is created."

    key = "Vessel Commands"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdBoard())
        self.add(CmdDebark())
        self.add(CmdSteer())
        # okay this is tedious but we neet a cmd from my Sea module
        self.add(CmdSetPosition())


class CmdSetLook(CmdSet):
    "Add this look command to the player when they enter the vessel"
    key = "Vessel Look"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdLookout())
# last line
