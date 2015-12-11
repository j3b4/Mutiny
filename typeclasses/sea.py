"""
The Sea Module
The Ocean rooms, the custom coastal rooms types, navigation commands
wind, currents and weather.  Whatever I can implement should go in here now
I hope.
"""

from evennia import CmdSet, Command, DefaultRoom


# Coastal Commands

class CmdFix(Command):
    """
    This returns the coordinates of the caller which should be set by coastal
    rooms when any object enters the room.
    """
    pass


class CmdSetPosition(Command):
    """
    Set the global position of a room.

    Usage:
        +setposition [<room>] [= x,y]

    Examples:
        +setposition Paris = 5,9
        +setposition Paris    ---> displays Paris's coordinates: 5, 9
        +setposition          ---> displays position of current room

    This sets the x,y coordinates or longitude and lattitude of the room
    named. 
    """

    key = "+setposition"
    aliases = ["+position", "+pos", "+setpos"]
    locks = "cmd:not perm(nonpcs)"
    help_category = "Mutinous"

    def parse(self):
        "Parse room and position arguments"
        args = self.args
        room, position = None, None
        # or should I start with room, position and then parse position into
        # x and y later?
        if "=" in args:
            # attempt to set the position
            # must be comma separated digits
            room, position = [part.strip() for part in args.rsplit("=", )]
            self.position = tuple(position)
            # is this allowed? Well no syntax error!
        self.room = room

    def func(self):
        "display position or set it."

        caller = self.caller
        # position = self.position

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
        if not self.position: # nothing to set just display rooms postition
            caller.msg("Position of '%s': %s" % target, target.position)
        else: # room target and position both supplied. Time to display.
            target.position = self.position
            caller.msg("New position of '%s': %s" %target, self.position)

class CoastalCmdSet(CmdSet):
    "This adds the coastal commands to be attached to coastal rooms"
    key = "Coastal Commands"
    priority = 1
    def at_cmdset_creation(self):
        self.add(CmdSetPosition())
        self.add(CmdFix())

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



"""
First costal command will be to go to sea. 
Board and Debark are connected to vessels. 
Not sure what other commands will be coastal only 
until I implement a higher level of coastal navigation.

later things like anchor, beach, dock, launch etc...
"""

# The Sea room
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
    pass

# Navigate Commands
class CmdNav(Command):
    """
    Ideally I would overload the "steer" command here to change its meaning
    slightly.  However for now I will make a seperate command "navigate"

    A useful debuggin cmd would be "fix" that could return an accurate set 
    of coordinates to allow accurate navigation. 

    """
    pass

