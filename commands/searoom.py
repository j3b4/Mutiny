# Sea Room Commands and Command Sets

from evennia import CmdSet, Command
from evennia.utils import search
# from evennia.utils import inherits_from
# from evennia.utils.create import create_object
import re

"""
These should apply to Sea Rooms
"""


class CmdFix(Command):
        """
        This returns the coordinates of the caller which should be set by
        coastal rooms when any object enters the room.

        Usage:
        fix <coordinates>

        E.G.:
        fix 6,7

        > At 6,7 is room #45

        """
        key = "fix"
        help_category = "Mutinous Commands"

        def func(self):
            "Ask the globe module to look in the atlas:"
            position = self.args
            if not position:
                print "usage: fix <x,y>"
                return
            print position, type(position)
            # must send a tuple to the globe module
            position = map(int, position.split(','))
            position = tuple(position)
            # "Find the room by searching the DB for an object"
            # "With the correct position attribute."
            room = search.search_object_attribute(key="coordinates",
                                                  value=position)
            self.caller.msg(room)


class CmdSetPosition(Command):
    """
    Set the global position of a room.

    Usage:
        +setposition [<room>] [= x,y]

    Examples:
        +setposition #4 = 5,9
        +setposition Paris    ---> displays Paris's coordinates: 5, 9
        +setposition          ---> displays position of current room

    This sets the x,y coordinates or longitude and lattitude of the room
    named.
    """

    key = "+setposition"
    aliases = ["+position", "+pos", "+setpos"]
    locks = "cmd:not perm(nonpcs)"
    help_category = "Mutinous Commands"

    def parse(self):
        "Parse room and position arguments"
        args = self.args
        room, coordinates = None, None
        # or should I start with room, position and then parse position into
        # x and y later?
        if "=" in args:
            self.caller.msg("Trying to set something...")
            # attempt to set the position
            # must be comma separated digits
            room, coordinates = [part.strip() for part in args.rsplit("=", )]
            self.caller.msg("Input Room = %s" % room)
            if not re.match(r'\d+,\d+', coordinates):
                self.caller.msg("Position must be entered in the form x,y.")
                return
            # coordinates come in as a string
            coordinates = map(int, coordinates.split(','))
            coordinates = tuple(coordinates)
            print("Position type = %s\n\n" % type(coordinates))
            self.caller.msg("Input pos = %s" % str(coordinates))
            # now convert string to tuple.

        else:
            # no '=' sign means we just want a report on rooms position.
            room = args
        # store stuff in DB
        self.room = room
        self.coordinates = coordinates

    def func(self):
        "display position or set it."

        caller = self.caller
        coordinates = self.coordinates

        if not self.args or not self.room:
            # get current room. Hmmm. (review 'look' for iseas)
            target = caller.location
            if not target:
                caller.msg(
                    "You need to be in a room to use this command!"
                    )
                return
        else:  # get target from the supplied argument
            target = caller.search(self.room)
            if not target:
                return
        # at this point we have a target

        if not coordinates:  # nothing to set just display rooms postition
            caller.msg("Coordinates of %s is %s" % (target.name,
                                                    target.db.coordinates))
        else:  # room target and position both supplied. Time to display.
            target.db.coordinates = coordinates
            caller.msg("New position of %s is %s" % (target.name,
                                                     target.db.coordinates))


class CoastalCmdSet(CmdSet):
    "This adds the coastal commands to be attached to coastal rooms"
    key = "Coastal Commands"
    priority = 1

    def at_cmdset_creation(self):
        pass


class NavCmdSet(CmdSet):
    key = "Navigiation Commands"
    pass
# Last line
