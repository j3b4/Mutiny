"""
Builder Commands

This set of builder commands for making Portage's special types of rooms
and all.

Stage one: simply modify @tunnel and @dig to require coordinates

"""

from django.conf import settings
from evennia.utils import create, search
from commands.command import MuxCommand
# from world.globe import COMPASS_ROSE


class CmdRaise(MuxCommand):
    """
    build new rooms and connect them to the current location
    based on the @dig command but "raises" land up out of the sea creating
    coastal rooms.

    Usage:
      @raise lon,lat roomname

      Switches:
        tel or teleport - move yourself to the new room
        inland          - new land will be DryLandRoom
        coast           - new land will be CoastalRoom

    Examples:
        @raise -04,-172,Kiribati Island
        > creates an island at 4S, 172S and names is Kiribati Island

        @raise/tel 51,000 Greenwich
        > creates an island at 51N, on the prime merdiian and teleports user
          to it

    This command does not create any exits since coastal rooms are meant to be
    entered from the sea by nautical movement.  Adjacent coastal or landlocked
    rooms should be created with "walk"


    """
    key = "@raise"
    aliases = ["rai", "@r"]
    help_category = "Portage Building"
    locks = "cmd:perm(dig) or perm(Builders)"

    def func(self):
        usage = "@raise lat,lon = Room Name"
        caller = self.caller

        if "," in self.lhs:
            for coord in self.lhslist:
                try:
                    int(coord)
                except ValueError:
                    usage = "\nOnly integers allowed"
                    usage += " for lat, lon.\n"
                    usage += " For example: @raise -17,177 = Fiji"
                    caller.msg(usage)
                    return
            lat, lon = self.lhslist  # `self.lhs` split into list by comma.
        else:
            caller.msg(usage)
            return

        # convert coordinates to int
        coordinates = (int(lat), int(lon))

        # search for matching coordinates in db
        conflict = search.search_object_attribute(key="coordinates",
                                                  value=coordinates)
        if conflict:
            report = "There is already a room at %s: %s"
            report += "\n%s is accessible as %s"
            report = report % (coordinates, conflict,
                               conflict[0].name, conflict[0].dbref)
            caller.msg(report)
            return

        # choose the typeclass
        if "inland" in self.switches:
            typeclass = "rooms.DryLandRoom"
            room = "Inland"
        else:
            typeclass = "rooms.CoastalRoom"
            room = "Coastline"

        # over write the default name if name was provided
        if self.rhs:
            room = self.rhs

        # create a room
        lockstring = "control:id(%s) or perm(Immortals); delete:id(%s)"
        lockstring += " or perm(Wizards); edit:id(%s) or perm(Wizards)"
        lockstring = lockstring % (caller.dbref, caller.dbref, caller.dbref)

        new_room = create.create_object(typeclass, room, report_to=caller)
        new_room.locks.add(lockstring)
        new_room.db.coordinates = coordinates  # save those coordinates
        room_string = "Created room %s(%s) of type %s." % (new_room,
                                                           new_room.dbref,
                                                           typeclass)
        caller.msg(room_string)
        if new_room and ('teleport' in self.switches
                         or "tel" in self.switches):
            caller.move_to(new_room)


class CmdWalk(MuxCommand):
    """
    based on the @tunnel command, creates coastal or landlocked rooms by
    walking in one of 8 directions.
    create new rooms in cardinal directions only

    Usage:
      @walk[/switch] <direction> [= roomname[;alias;alias;...]

    Switches:
      oneway - do not create an exit back to the current location
      still - do not teleport to the newly created room
      inland - new room will be DryLandRoom*
      coast -  new room will be a CoastalRoom*
        * the default is to create a room of the same type as the i
          starting room.


    Example:
      @walk n
      @walk n = house

    This is a simple way to build using pre-defined directions:
    The full names (north, in, southwest, etc) will always be put as
    main name for the exit, using the abbreviation as an alias (so an
    exit will always be able to be used with both "north" as well as
    "n" for example). Opposite directions will automatically be
    created back from the new room unless the /oneway switch is given.

    The important distcintion from @tunnel is that @walk automatically adds
    coordinates to new rooms. If walking in a certain direction would conflict
    with a pre-existing room, the user should be prompted to abort, connect, or
    overwrite the existing room.

    """
    key = "walk"
    aliases = ["wlk", "+w"]
    help_category = "Portage Building"
    locks = "cmd: perm(tunnel) or perm(Builders)"

    # store the direction, full name and its opposite and vector
    # The idea is to add the vector to starting coordinates to
    # obtain coordinates for the target room.
    # directions{direction}[0] = long_name
    # directions{direction}[1] = back
    # directions{direction}[2] = vector
    directions = {"n": ("north", "s", (1, 0)),
                  "ne": ("northeast", "sw", (1, 1)),
                  "e": ("east", "w", (0, 1)),
                  "se": ("southeast", "nw", (-1, 1)),
                  "s": ("south", "n", (-1, 0)),
                  "sw": ("southwest", "ne", (-1, -1)),
                  "w": ("west", "e", (0, -1)),
                  "nw": ("northwest", "se", (1, -1)),
                  }

    def func(self):
        caller = self.caller
        location = caller.location
        old_coord = location.db.coordinates  # lat,lon of starting room
        if not old_coord:
            string = ("%s has no coordinates we cannot use 'walk' from here")
            string = string % location
            caller.msg(string)
            return
        "Implements the walk command"
        if not self.args or not self.lhs:
            string = "Usage: @walk[/switch] <direction> "
            string += "[= roomname]"
            self.caller.msg(string)
            return
        if self.lhs not in self.directions:
            string = "@walk only works in the following directions: %s."
            string = string % ",".join(sorted(self.directions.keys()))
            string += "\n(use @dig or @raise for more freedom)"
            self.caller.msg(string)
            return
        # retrieve all input and parse it
        sd = self.directions
        ex = self.lhs
        exname, back = sd[ex][0], sd[ex][1]
        backname = sd[back][0]
        string = "backname = %s" % backname
        vector = sd[ex][2]
        # caller.msg("Vector for %s is %s" % (ex, vector))
        caller.msg(string)
        string = ""

        # calculate location of new_coord for new room
        new_coord = (old_coord[0] + vector[0],
                     old_coord[1] + vector[1])

        # search for matching coordinates in db
        conflict = search.search_object_attribute(key="coordinates",
                                                  value=new_coord)
        if conflict:
            report = "There is already a room at %s: %s"
            report += "\n%s is accessible as %s"
            report = report % (new_coord, conflict,
                               conflict[0].name, conflict[0].dbref)
            report += "\nSo you can delete it now then re-run this"
            report += "command, or just try to link to it.\n"
            report += "Automating this is on my todo list."
            caller.msg(report)
            return

        # find the backwards exit from the directions
        # backstring = ", %s;%s" % (backname, back)

        # choose the typeclass
        if "inland" in self.switches:
            typeclass_path = "rooms.DryLandRoom"
            roomname = "Inland"
        elif "coast" in self.switches:
            typeclass_path = "rooms.CoastalRoom"
            roomname = "Coastline"
        else:
            # no switches  default type and name of start room
            # but name can be over written
            typeclass_path = location.typeclass_path
            roomname = location.name

        # name the new room
        if self.rhs:
            roomname = self.rhs  # this may include aliases; that's fine.

        # create room
        lockstring = "control:id(%s) or perm(Immortals); delete:id(%s) "
        lockstring += "or perm(Wizards); edit:id(%s) or perm(Wizards)"
        lockstring = lockstring % (caller.dbref, caller.dbref, caller.dbref)
        new_room = create.create_object(typeclass_path, roomname,
                                        report_to=caller)

        # lock the room after creation
        new_room.locks.add(lockstring)

        # add the coordinates
        new_room.db.coordinates = new_coord

        room_string = "Created room %s(%s) of type %s." % (
            new_room, new_room.dbref, typeclass_path)

        # create exit to room
        # Build the exit to the new room from the current one
        xtc = settings.BASE_EXIT_TYPECLASS

        new_to_exit = create.create_object(xtc, exname,
                                           location,
                                           aliases=ex[0],
                                           locks=lockstring,
                                           destination=new_room,
                                           report_to=caller)
        alias_string = ""
        exit_to_string = "\nCreated Exit from %s to %s: %s(%s)%s."
        exit_to_string = exit_to_string % (location.name,
                                           new_room.name,
                                           new_to_exit,
                                           new_to_exit.dbref,
                                           alias_string)
        # Create exit back from new room
        # Building the exit back to the current room
        if not location:
            exit_back_string = \
                "\nYou cannot create an exit back to a None-location."
        else:
            typeclass = settings.BASE_EXIT_TYPECLASS
            new_back_exit = create.create_object(typeclass,
                                                 backname,
                                                 new_room,
                                                 aliases=back,
                                                 locks=lockstring,
                                                 destination=location,
                                                 report_to=caller)
            alias_string = ""
            exit_back_string = "\nCreated Exit back from %s to %s: %s(%s)%s."
            exit_back_string = exit_back_string % (new_room.name,
                                                   location.name,
                                                   new_back_exit,
                                                   new_back_exit.dbref,
                                                   alias_string)
        caller.msg("%s%s%s" % (room_string, exit_to_string, exit_back_string))
        if new_room and ('still' not in self.switches):
            caller.move_to(new_room)


class CmdWind(MuxCommand):
    """
    Set the wind direction and speed property on the global wind script.
    Direction is in degrees and speed in knots.

    usage: +setwind/<switches> <direction> <speed>
    """
    key = "+setwind"
    aliases = ["+wind", ]
    help_category = "Portage Building"
    locks = "perm(Builders)"

    def func(self):
        matches = search.search_script("WorldWind")
        print "\nmatches = %s, type = %s" % (matches, type(matches))
        if not matches:
            print "No match in the db for WorldWind.\n"
            return
        WorldWind = matches[0]
        print "WorldWind type = %s\n\n" % type(WorldWind)

        if not self.args:
            (direction, speed) = WorldWind.return_wind((1, 1))
            string = "The wind is blowing %s degrees at %s knots"
            self.caller.msg(string % (direction, speed))
            return
        elif self.switches:
            print "Do stuff with switches"
        else:
            print "This suggests there were some arguments"
            [direction, speed] = self.lhs.split()
            # now set the wind on the object
            string = "You set the wind to %s degrees at %s knots"
            self.caller.msg(string % (direction, speed))
            WorldWind.set_wind(direction, speed)
        # switches:
        # /direction = single arguemnt is a direction
        # /speed = single argument is speed
        # single arg can me a direction name without switches

        # two arg is always direction then speed

        # confirm before setting


class CmdCurrent(MuxCommand):
    """
    Set the current direction and speed property on the global script.
    Direction is in degrees and speed in knots.

    usage: +setcurrent/<switches> <direction> <speed>
    """
    key = "+setcurrent"
    aliases = ["+current", ]
    help_category = "Portage Building"
    locks = "perm(Builders)"

    def func(self):
        matches = search.search_script("WorldWind")
        print "\nmatches = %s, type = %s" % (matches, type(matches))
        if not matches:
            print "No match in the db for WorldWind.\n"
            return
        WorldWind = matches[0]
        print "WorldWind type = %s\n\n" % type(WorldWind)

        if not self.args:
            (direction, speed) = WorldWind.return_current((1, 1))
            string = "The current is flowing %s degrees at %s knots"
            self.caller.msg(string % (direction, speed))
            return
        elif self.switches:
            print "Do stuff with switches"
        else:
            print "This suggests there were some arguments"
            [direction, speed] = self.lhs.split()
            # now set the wind on the object
            string = "You set the current to %s degrees at %s knots"
            self.caller.msg(string % (direction, speed))
            WorldWind.set_current(direction, speed)


class CmdBoardingArea(MuxCommand):
    '''
    Use this command on a vessel to set it's default boarding area. That is
    the place on the vessel that the player will be delivered to upon
    "boarding".

    Usage:
      @boardingarea <vessel> <shipstation>

    '''
    key = "@boardingarea"
    aliases = ["@board", "@ba"]
    help_category = "Portage Building"
    locks = "cmd:perm(dig) or perm(Builders)"

    def func(self):
        '''get arguments from command line, add an attribute to target'''
        if not self.args:
            string = "Usage: @setboardingarea <vessel> <shipstation>"
            self.caller.msg(string)
            return
        vessel = self.caller.search(self.lhs, global_search=True)
        if not vessel:
            return
        if not self.rhs:
            # just view the boarding area
            boarding_area = vessel.db.boarding_area
            if not boarding_area:
                string = "The %s has no boarding area set." % vessel.name
            else:
                string = "The %s's boarding area is %s(%s))."
                string = string % (vessel, boarding_area, boarding_area.dbref)
        else:
            # set a new boarding area
            new_ba = self.caller.search(self.rhs, global_search=True)
            if not new_ba:
                return
            old_ba = vessel.db.boarding_area
            vessel.db.boarding_area = new_ba
            if old_ba:
                string = "%s's boading area changed from %s(%s) to %s(%s)."
                string = string % (vessel, old_ba, old_ba.dbref, new_ba,
                                   new_ba.dfref)
            else:
                string = "%s' boarding area set to %s(%s)."
                string = string % (vessel, new_ba, new_ba.dbref)
        self.caller.msg(string)


# Last line
