"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from commands.searoom import CoastalCmdSet
from commands.searoom import NavCmdSet


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    pass


class SeaRoom(Room):
    'Common Parent of master and dynamic sea rooms if needed.'
    def at_object_creation(self):
        self.cmdset.add_default(NavCmdSet)
        self.db.coordinates = None
        self.tags.add("searoom")

    def at_object_receive(self, new_arrival, source_location):
        new_arrival.db.position = self.db.coordinates
        pass


class DynamicRoom(SeaRoom):
    '''
    Probably all the action should take place here. That is the DSR is the only
    room that players should ever see.  So for instance the command sets should
    apply here etc.
    '''
    pass


# Coastal Rooms
class CoastalRoom(SeaRoom):
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

        # debugging messages
        self.msg_contents(
            "%s arrives in this room %s"
            % (new_arrival.name, position))
        new_arrival.msg_contents("%s arrives in this room %s"
                                 % (new_arrival.name, position))
        # set position on new arrival
        new_arrival.db.position = position

        pass

# Last line
