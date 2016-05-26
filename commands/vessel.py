# Commands for Ships and Boats etc.

from evennia import default_cmds
from evennia import CmdSet, Command
from world.globe import measure, move_vector
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
    aliases = ["embark", "go onboard", "come aboard", ]
    help_category = "Mutinous Commands"
    locks = "cmd:not cmdinside()"

    # adding a parser? or something to allow multiple vessels in one room.
    def parse(self):
        self.target = self.args.strip()

    def func(self):
        if not self.target:
            self.caller.msg("Usage: board <vessel>")
            return
        else:
            vessel = self.caller.search(self.target)
            if not vessel:
                # caller.search handles error messages. Thanks!
                return
            if not vessel.is_typeclass("vessel.VesselObject"):
                self.caller.msg("You cannot board the %s." % vessel)
                return
            self.caller.msg("You to board the %s" % vessel)
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
            vessel = caller.location
            outside = vessel.location
            " First copy default look function"
            if not self.args:
                target = vessel
                if not target:
                    caller.msg("No location to look at!")
                    return
                # no args means this is where the vessel look should sit.
                outboard_view = (vessel.at_look(outside))
                # TODO: Process the outboard_view, strip out exits.
                inboard_view = caller.at_look(target)
                caller.msg("You're on the %s" % vessel.key)
                # caller.msg("Outside you see:")
                caller.msg(outboard_view)
                # caller.msg("Inside you see:\n")
                caller.msg(inboard_view)
            else:
                # if there are arguemnts then do a standard look on them
                target = caller.search(self.args)
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
    key = "conn"
    help_category = "Mutinous Commands"
    aliases = ["take the helm", ]

    def func(self):
        captain = self.caller
        vessel = captain.location
        captain.cmdset.add(CmdSetConn, permanent=True)
        captain.msg("You take the Conn.")
        vessel.msg_contents("%s takes the Conn!" % captain)


class CmdNorth(Command):
    """
    This command moves the vessel in the direction stated.

    Usage: North
        Note you have to use this command with "steer" if you are onboard a
        vessel.
    """  # % key

    key = "north"
    aliases = ["n", ]
    help_category = "Mutinous Commands"
    # auto_help = False   # so we can create a dynamic help strings
    # translate direction into a vector
    vector = (1, 0)

    def func(self):
        # get the direction
        captain = self.caller
        vessel = self.caller.location
        key = self.key
        vector = self.vector

        # get position
        position = vessel.db.position
        if not position:
            string = ("AVAST! %s lacks a starting position" % vessel)
            string += " navigation impossible!"
            vessel.msg_contents(string)
            return
        # vessel.msg_contents("original position = %s" % position)

        # parse
        vessel.msg_contents("%s steers the %s %s" % (captain, vessel, key))

        # add vector to position
        position = ((position[0] + vector[0]), (position[1] + vector[1]))

        # announce results
        vessel.msg_contents("New position = %s" % str(position))

        # Arrive at
        self.obj.arrive_at(vessel, position)

        # Old arrival Code - now moved to Globe
        '''
            # The following code moves a vessel to a new position and room that
            # matches that position.  It should be taken out and packaged in
            # another function.
            # ARRIVE AT

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
                                    % str(position))
                vessel.location.db.coordinates = position
                # have to update vessel position to match rooms new position
                vessel.db.position = position
                return
            else:  # Assume the current room is occupied or not dynamic
                # create the room
                vessel.msg_contents("Creating new room at %s" % str(position))
                room = create_object(typeclass="rooms.DynamicRoom",
                                    key="The Open Ocean",
                                    location=None,
                                    )
                room.db.coordinates = position
                vessel.msg_contents("Moving to %s" % room)
                vessel.move_to(room)
                return
            '''
        print "Something else went wrong"


class CmdSouth(CmdNorth):
    key = "south"
    aliases = ["s", ]
    vector = (-1, 0)


class CmdEast(CmdNorth):
    key = "east"
    aliases = ["e", ]
    vector = (0, 1)


class CmdWest(CmdNorth):
    key = "west"
    aliases = ["w", ]
    vector = (0, -1)


class CmdNorthEast(CmdNorth):
    key = "northeast"
    aliases = ["ne", ]
    vector = (1, 1)


class CmdNorthWest(CmdNorth):
    key = "northwest"
    aliases = ["nw", ]
    vector = (1, -1)


class CmdSouthEast(CmdNorth):
    key = "southeast"
    aliases = ["se", ]
    vector = (-1, 1)


class CmdSouthWest(CmdNorth):
    key = "southwest"
    aliases = ["sw", ]
    vector = (-1, -1)


class CmdGlobalMeasure(Command):
    """
    Measure the distance between two points on the globe.

    Usage:
        measure lat,lon & lat,lon

    Example:
        measure 0,5 & 6,6
        measure -42,39 & -2,41

    This command lets the user of the conn measure the distance between any two
    points of latitude and longitude
    """

    key = "measure"
    help_category = "Mutinous Commands"
    aliases = ["distance between", ]

    def parse(self):
        """
        Parse the input for 2 points with 2 coordinates each
        """
        caller = self.caller
        report = caller.msg
        args = self.args
        # report(args)
        if "&" in self.args:
            # point_a, point_b = None, None
            point_a, point_b = [part.strip() for part in args.split("&")]
            if not point_a or not point_b:
                report("Usage: measure lat,long & lat,long")
                return

            # convert to lists or tuples
            a = tuple(map(float, point_a.split(',')))
            b = tuple(map(float, point_b.split(',')))
            report("Points:  a = %s and b = %s" % (a, b))
            self.a = a
            self.b = b
        else:
            report("Usage: measure lat,long & lat,long")
            return

    def func(self):
        caller = self.caller
        report = caller.msg
        # if not self.a or not self.b:
        #    report("Usage: measure lat,long & lat,long")
        #    return
        a = self.a
        b = self.b
        distance = measure(a, b)
        report("From %s to %s is %s nautical miles" % (a, b, distance))


# from world.globe import measure, travel
class CmdTravel(Command):
    """
    Accept an initial heading 3 figure degrees and distance in nautical miles
    from the conning player.  Then move the vessel that distance following a
    great circle course.

    # figure notation means include a 3 digits even if you have to use leading
    zer
    Ie.  North = 000, (or 360)
        East = 090
        South = 180
        West = 270

    Usage:
        travel <heading> <distance>   (help travel for details)

    Example:
        assume vessel is starting at Null Island (0N, 0E):
        travel 090 120

        Result:
            The vessel will move 120 nautical miles East and end up at
            coordinates: (0N, 2E)
    """

    key = "travel"
    help_category = "Mutinous Commands"
    aliases = ["move", "tr"]
    usage = "travel <heading> <distance>   (help travel for details)"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg(self.usage)
            return
        self.heading, self.distance = self.args.split()
        vessel = caller.location
        report = caller.msg
        heading = int(self.heading)
        print heading
        distance = float(self.distance)
        print distance

        report("You set a heading of %s, and travel %s nautical miles"
               % (str(heading), str(distance)))

        start_position = (tuple(vessel.db.position))
        # start_position = (0, 0)
        report("given a starting position of %s" % str(start_position))

        final_position = move_vector(start_position, (heading, distance))

        report("You will arrive at %s" % str(final_position))

        # Lets see if arrive at works out of the box:
        self.obj.arrive_at(vessel, final_position)


# script based movement
class CmdGetUnderway(Command):
    """
    ROW! A single command which orders the current ship to start moving in
    what ever direction is is already pointing. Once underway, it is possible
    to adjust the heading with the steer command. Row takes one argument an
    integer representing speed in knots.

    Usage:
        row <speed>

    Example:
        row 60

    Result:
        The boat starts moving at 60kts in current direction, use steer to
        change heading.
    """
    key = "row"
    help_category = "Mutinous Commands"
    aliases = ["power", ]
    usage = "row <speed>"

    def func(self):
        vessel = self.obj.location
        heading = vessel.db.heading
        if self.args:
            speed = int(self.args)
            "call the get underway function on the vessel object"
            vessel.get_underway(speed)
            string = "The %s starts moving at %skts, heading %s"
            string = string % (vessel, speed, heading)
        else:
            string = "Supply a speed in knots.\n" + self.usage
        vessel.msg_contents(string)


class CmdHeaveTo(Command):
    """
    A single command that halts the ship.
    Usage: hold
    """
    key = "hold"
    aliases = ["heave to", ]
    help_category = "Mutinous Commands"
    usage = "hold"

    def func(self):
        vessel = self.obj.location
        vessel.msg_contents("You call HOLD! to stop the rowing.")
        vessel.heave_to()


class CmdWeighAnchor(Command):
    """
    Cancels the anchor, set the vessel adrift and starts the ticker again.
    Subjecting the vessel to wind and current forces.
    """
    key = "weigh anchor"
    aliases = ["weigh", "raise anchor", "cast off"]
    help_category = "Mutinous Commands"
    usage = "weigh anchor"

    def func(self):
        vessel = self.obj.location
        vessel.msg_contents("You weigh anchor, and are now adrift")
        vessel.cast_off()


class CmdAnchor(Command):
    """
    Drop anchor to stop drifting or rowing.

    Usage: anchor
    """
    key = "anchor"
    help_category = "Mutinous Commands"
    usage = "anchor"

    def func(self):
        vessel = self.obj.location
        vessel.msg_contents("You heave anchor")
        vessel.anchor()


class CmdSteerTo(Command):
    """
    A two part command. Steer takes a direction as an argument and translates
    it into a three digit compass heading

    Usage: "steer <heading>"

    Example:
        > steer 000
        >> (points the vessel North)

        > steer 225
        >> points the vessel Southwest
    """
    key = "steer"
    aliases = ["bear", "head", "point", ]
    help_category = "Mutinous Commands"
    usage = "steer <heading>"

    def parse(self):
        "parse the directional argument"
        self.heading = self.args.strip()

    def func(self):
        "set the heading attribute"
        helm = self.obj
        vessel = self.obj.location
        if self.heading:
            vessel.steer_to(self.heading)
            string = "%s steers the %s to %s!" % (helm, vessel, self.heading)
        else:
            string = "Current heading: %s" % vessel.db.heading
        vessel.msg_contents(string)


class CmdSails(Command):
    '''
    Sails commands allows sails to be set or furled. Later reefing might be
    posible.

    Usage: "sails <up/down>"

    When sails go up, they will automatically be set to make the best course on
    current heading and wind angle. Setting sails in irons will automatically
    heave to.
    '''
    key = "sails"
    aliases = ["sail", ]
    help_category = "Mutinous Commands"
    usage = "Usage: sails <up/down>"

    def func(self):
        vessel = self.obj.location
        order = self.args.strip()
        canvas = vessel.db.sails
        if not order:
            vessel.msg_contents("Sails are at %s" % canvas)
        elif order == "up":
            vessel.db.sails = 1.0
            vessel.msg_contents("Sails are at %s" % vessel.db.sails)
        elif order == "down":
            vessel.db.sails = 0
            vessel.msg_contents("Sails are at %s" % vessel.db.sails)
        else:
            vessel.msg_contents(self.usage)


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
    #
    # Adding global measurements and movemnt commands
    pass
    key = "Conning Commands"
    priority = 2

    def at_cmdset_creation(self):
        self.add(CmdTravel())
        # I removed the direct movement commands.
        self.add(CmdGetUnderway())
        self.add(CmdHeaveTo())
        self.add(CmdSteerTo())
        self.add(CmdAnchor())
        self.add(CmdWeighAnchor())
        self.add(CmdSails())


class CmdSetVessel(CmdSet):
    "Add these commands to the vessel when it is created."
    key = "Vessel Commands"
    priority = 1
    duplicates = False

    def at_cmdset_creation(self):
        self.add(CmdDebark())
        self.add(CmdBoard())
        self.add(CmdGlobalMeasure())
        # add the conn command below
# last line
