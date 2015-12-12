"""
The Sea Module
The Ocean rooms, the custom coastal rooms types, navigation commands
wind, currents and weather.  Whatever I can implement should go in here now
I hope.
"""
import re
from evennia import CmdSet, Command, DefaultRoom


# Coastal Commands

class CmdFix(Command):
    """
    This returns the coordinates of the caller which should be set by coastal
    rooms when any object enters the room.
    """
    key = "+fix"
    help_category = "Mutinous Commands"

    pass

class CmdStandOff(Command):
    """
    To move away from shore.

    Usage:
        standoff
        steer offshore
    """
    key = "standoff"
    # aliases = ["offshore", "out to sea"]
    help_category = "Mutinous Commands"

    def func(self):
        "Move the caller to the sea room"
    pass

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
        room, position = None, None
        # or should I start with room, position and then parse position into
        # x and y later?
        if "=" in args:
            self.caller.msg("Trying to set something...")
            # attempt to set the position
            # must be comma separated digits
            room, position = [part.strip() for part in args.rsplit("=", )]
            # self.caller.msg("Input Room = %s" % room)
            # self.caller.msg("Input pos = %s" % position)
            if not re.match(r'\d+,\d+', position):
                self.caller.msg( "Position must be entered in the form x,y.")
                return
        self.room = room
        self.position = position

    def func(self):
        "display position or set it."

        caller = self.caller
        position = self.position

        if not self.args or not self.room:
            # get current room. Hmmm. (review 'look' for iseas)
            target = caller.location
            if not target:
                caller.msg(
                    "You need to be in a room to use this command!"
                    )
                return
        else: # get target from the supplied argument
            target = caller.search(self.room)
            if not target:
                return
        # at this point we have a target 

        if not position: # nothing to set just display rooms postition
            caller.msg("Position of %s is %s" % (target.name, 
                target.db.position))
        else: # room target and position both supplied. Time to display.
            target.db.position = position
            caller.msg("New position of %s is %s" % (target.name, 
                    target.db.position))

class CoastalCmdSet(CmdSet):
    "This adds the coastal commands to be attached to coastal rooms"
    key = "Coastal Commands"
    priority = 1
    def at_cmdset_creation(self):
        self.add(CmdSetPosition())
        self.add(CmdFix())
        self.add(CmdStandOff)

# Coastal Rooms
class CoastalRoom(DefaultRoom):
    """
    Coastal rooms need to be defined with co-ordinates so that they
    can pass that to vessels that leave them for the sea room giving the 
    vessel its starting position at Sea.

    Finally the Sea will need to know where everyroom is so as to deliver 
    vessels to the right coastal room as an exit.

    Also I'd like Coastal rooms to have a tag that makes them passable 
    by vessels. Default rooms can be presumed to be landrooms and not 
    so passable.  Rivers would make an interesting subset of this.
    """
    def at_object_creation(self):
        self.db.coastline = ""
        self.db.position = (None, None)
        # add the command set
        self.cmdset.add_default(CoastalCmdSet)

    def at_object_receive(self, new_arrival, source_location):
        """
        We need to give the arrival our coordinates when then arrive.
        Set the new arrivals position to match the rooms
        """

        position = self.db.position

        #debugging messages
        self.msg_contents(
                "%s arrives in this room %s" 
                % (new_arrival.name, position))
        new_arrival.msg_contents(
                "%s arrives in this room %s" 
                % (new_arrival.name, position))
        # set position on new arrival
        new_arrival.db.position = position

        pass


"""
First coastal command will be to go to sea. 
Board and Debark are connected to vessels. 
Not sure what other commands will be coastal only 
until I implement a higher level of coastal navigation.

later things like anchor, beach, dock, launch etc...
"""



# The Sea room
# Sea Room Commands

class CmdNavTo(Command):
    """
    This is a magic navigation command that simply sets the vessels
    coordinates. Could just as reasonably be attached to the vessel.

    for testing might be redundand as long as user can use +setpos
    """
    pass

class CmdLandFall(Command):
    """
    Make Landfall - to display available exit to a coastal room and
    or move the caller to the coastal room that matches its current
    position.

    Usage:
        landfall
    """
    key = "landfall"
    alisases = ["lf",]
    help_category = "Mutinous Commands"

    def func(self):
        sailor = self.caller
        sea = sailor.location
        position = sailor.db.position
        globe = sea.db.globe

        if position in globe:
            coast_num = globe[position]
            # need to get the object 
            coast_room = self.caller.search(coast_num)
            sailor.msg("You would land at %s(%s)" % 
                    (coast_room.name, coast_num))

        else:
            sailor.msg("Nothing here but water, everywhere.")


    # get callers position

    # look position up in globe dictionary

    # move caller there.
    pass



class NavCmdSet(CmdSet):
    "This adds the Navigation commands to be attached to sea rooms"
    key = "Navigation Commands"
    priority = 1
    def at_cmdset_creation(self):
        self.add(CmdSetPosition())
        self.add(CmdLandFall())
        self.add(CmdFix())

class SeaRoom(DefaultRoom):
    """
    If this even needs to be a room. Oh yes b/c it has no location itself.

    The sea itself doesn't actuall have coordiniates does it?  Instead it 
    tracks the coord of objects within it - vessesl. It also delivers up exits
    to vessels depening on their coordinates.

    Well some object has to store this so for now it might as well be the Sea
    room. In the future I'd want newly created coastal rooms to automatically
    report their coordinates to a db somewhere.
    """
    def at_object_creation(self):
        "hmmm"
        self.db.globe = {'8,4':'#4', '6,4':'#8','7,3':'#5'}
        # the globe is a dictionary of coordinates and room references
        # right now hard coded with three locations
        self.cmdset.add_default(CoastalCmdSet)
        self.cmdset.add_default(NavCmdSet)

    def at_object_receive(self, new_arrival, source_location):
        "Note where the arrival came from. Maybe add to db?"
        position = new_arrival.db.position
        self.msg_contents( "%s arrives at Sea from %s(%s)" 
                % (new_arrival.name, source_location, position))
        new_arrival.msg_contents( "%s arrives at Sea from %s(%s)" 
                % (new_arrival.name, source_location, position))
        #


