# Commands for Ships and Boats etc.

from evennia import default_cmds
from evennia import CmdSet, Command
from evennia.utils import search
from evennia.utils import inherits_from
from evennia.utils.create import create_object

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
            # TODO: Process the outboard_view, strip out exits.
            inboard_view = self.caller.at_look(target)
            caller.msg("You're on the %s" % vessel.key)
            # caller.msg("Outside you see:")
            caller.msg(outboard_view)
            # caller.msg("Inside you see:\n")
            caller.msg(inboard_view)
        else:
            # if there are arguemnts then do a standard look on them
            target = self.caller.search(self.args)
            if not target:
                return
            self.msg(caller.at_look(target))


class CmdConn(Command):
    """
    Take control of the vessel

    Usage:
        conn

    This allows you to direct the vessel instantly in 8 directions.
    """
    key = "Conn"
    help_category = "Mutinous Commands"
    aliases = ["take the helm", ]

    def func(self):
        captain = self.caller
        captain.cmdset.add(CmdSetConn, permanent=True)

        # self.cmdset.add(CmdSetOnboard, permanent=True)


class CmdNorth(Command):
    key = "north"

    """
    This command moves the vessel in the direction stated.

    Usage: <%s>
        Note you have to use this command with "steer" if you are onboard a
        vessel.
    """ % key

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
        vessel.msg_contents("original position = %s" % position)

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
            # If the destination room exists, we go there.
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
                vessel.msg_contents("Moving to %s" % room)
                vessel.move_to(room)
                return
        elif (vessel.location.is_typeclass("rooms.DynamicRoom") and
                len(vessel.location.contents) == 1):
            # This means we are in a dynamic room alone
            vessel.msg_contents("updating room coordinates to %s"
                                % position)
            vessel.location.db.coordinates = position
            # have to update vessel position to match rooms new position
            vessel.db.position = position
            return
        elif len(vessel.location.contents) > 1:
            vessel.msg_contents("but there are objects in this room")
            # create the room
            vessel.msg_contents("Creating new room at %s" % position)
            room = create_object(typeclass="rooms.DynamicRoom",
                                 key=str("dynasea"),
                                 location=None,
                                 )
            room.db.coordinates = position
            vessel.msg_contents("Moving to %s" % room)
            vessel.move_to(room)
            return
        print "Something else went wrong"


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


class CmdSetOnboard(CmdSet):
    "Add this look command to the player when they enter the vessel"
    # TODO: Consider moving this to conning set, to simulate the requirement to
    # get up on the conning tower to be able to realls see out there.

    key = "Onboard Commands"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdLookout())
        self.add(CmdConn())


class CmdSetConn(CmdSet):
    "This adds the Conning commands to be attached to sea rooms"
    # These commands control the entire ship in a powerful "driving mode"
    # In the future they might be unavailable ot regular users. Since they
    # allow instant movement in any direction on the grid.
    pass
    key = "Conning Commands"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdNorth())
        self.add(CmdSouth())
        self.add(CmdEast())
        self.add(CmdWest())
        self.add(CmdNorthEast())
        self.add(CmdNorthWest())
        self.add(CmdSouthEast())
        self.add(CmdSouthWest())


class CmdSetVessel(CmdSet):
    "Add these commands to the vessel when it is created."
    key = "Vessel Commands"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdBoard())
        self.add(CmdDebark())
        # add the conn command below
# last line
