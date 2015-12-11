"""
The Sea Module
The Ocean rooms, the custom coastal rooms types, navigation commands
wind, currents and weather.  Whatever I can implement should go in here now
I hope.
"""

from evennia import CmdSet, Command, DefaultRoom

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
        self.db.lat = None
        self.db.lon = None

    def fix_location(self):
        return self.db.lon, self.db.lat


# Coastal Commands

class FixCmd(Command):
    """
    This returns the coordinates of the caller which should be set by coastal
    rooms when any object enters the room.
    """
    pass


class SetPosition(Command):
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
        room, lon, lat = None, None, None
        # or should I start with room, position and then parse position into
        # x and y later?
        if "=" in args:
            # attempt to set the position
            # must be comma separated digits
            room, 




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

