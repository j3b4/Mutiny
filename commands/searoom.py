# Sea Room Commands and Command Sets

from evennia import CmdSet, Command
from evennia.utils import search
from evennia.utils import inherits_from
from evennia.utils.create import create_object
import re

"""
These should apply to Sea Rooms and to Master Sea Rooms
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


class CmdNorth(Command):
    """
    This command moves the vessel in the direction stated.

    Usage: <steer> <direction>
        Note you have to use this command with "steer" if you are onboard a
        vessel.
    """

    key = "north"
    aliases = ["n", ]
    help_category = "Mutinous Commands"
    # translate direction into a vector
    vector = (0, -1)

    def func(self):
        # get the direction
        vessel = self.caller
        key = self.key
        vector = self.vector

        # get position
        position = vessel.db.position
        print "original position = %s" % position

        # parse
        vessel.msg_contents("Heading %s" % key)

        # add vector to position
        position = [(position[0] + vector[0]), (position[1] + vector[1])]

        # announce results
        vessel.msg_contents("New position = %s" % str(position))

        # Look up room then move to it or create it and move to it
        # Look up room
        room = search.search_object_attribute(key="coordinates",
                                              value=position)
        # move to room
        if room:
            # If the room exists, we go there.
            vessel.msg_contents("%s already exists." % room)
            room = room[0]
            # TODO: fix this^ throw on multimatch rooms there should only
            # ever be one room per coordinates
            # unless it is dry land
            if inherits_from(room, "typeclasses.rooms.DryLandRoom"):
                vessel.msg_contents("It's dry land so cancelling move.")
                return
            # but if not dry land... lets get on with it and move
            else:
                print "The room at %s is navigable." % position
            vessel.msg_contents("Moving to %s" % room)
            vessel.move_to(room)
            vessel.db.position = position
            # not sure why I need this since the room should provide pos.
        elif vessel.location.is_typeclass("rooms.DynamicRoom"):
            # The target room does not exists AND we are in a Dynamic room.
            # starting in a dynaroom means that the room changes coordinates
            # but we don't change rooms.
            vessel.msg_contents("updating room coordinates to %s" % position)
            vessel.location.db.coordinates = position
            # have to update vessel position to match rooms new position
            vessel.db.position = position

        else:
            # create the room
            vessel.msg_contents("Creating the room at %s" % position)
            room = create_object(typeclass="rooms.DynamicRoom",
                                 key=str("dynasea"),
                                 location=None,
                                 )
            room.db.coordinates = position
            vessel.msg_contents("Moving to %s" % room)
            vessel.move_to(room)


class CmdSouth(CmdNorth):
    key = "south"
    aliases = ["s", ]
    vector = (0, 1)


class CmdEast(CmdNorth):
    key = "east"
    aliases = ["e", ]
    vector = (1, 0)


class CmdWest(CmdNorth):
    key = "west"
    aliases = ["w", ]
    vector = (-1, 0)


class CmdNorthEast(CmdNorth):
    key = "northeast"
    aliases = ["ne", ]
    vector = (1, -1)


class CmdNorthWest(CmdNorth):
    key = "northwest"
    aliases = ["nw", ]
    vector = (-1, -1)


class CmdSouthEast(CmdNorth):
    key = "southeast"
    aliases = ["se", ]
    vector = (1, 1)


class CmdSouthWest(CmdNorth):
    key = "southwest"
    aliases = ["sw", ]
    vector = (-1, 1)


class NavCmdSet(CmdSet):
    "This adds the Navigation commands to be attached to sea rooms"
    key = "Navigation Commands"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdSetPosition())
        self.add(CmdFix())
        self.add(CmdNorth())
        self.add(CmdSouth())
        self.add(CmdEast())
        self.add(CmdWest())
        self.add(CmdNorthEast())
        self.add(CmdNorthWest())
        self.add(CmdSouthEast())
        self.add(CmdSouthWest())


class CoastalCmdSet(CmdSet):
    "This adds the coastal commands to be attached to coastal rooms"
    key = "Coastal Commands"
    priority = 1

    def at_cmdset_creation(self):
        pass

# Last line
