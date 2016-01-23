"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from commands.default_cmdsets import ChargenCmdset


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


class ChargenRoom(Room):
    """
    This room class is used by character-generation rooms. It makes
    the ChargenCmdset available.
    """
    def at_object_creation(self):
        "This is called only at first creation."
        self.cmdset.add(ChargenCmdset, permanent=True)


class SeaRoom(Room):
    'Common Parent of master and dynamic sea rooms if needed.'
    pass


class MasterSeaRoom(SeaRoom):
    '''
    Every coastal room with the exit "offshore" or equivalent should
    lead to this room (the MSR).  However if any vessel enters
    the MSR it should trigger a dynamic sea room (DSR) to spawn and the
    vessel be immediately moved to the new DSR. The DSR will have a set of
    coordinates derived from the originating coastal room.

    If the coordinates of the to be spawned DSR match an existing DSR, then no
    new room should spawn and instead the vessel should be moved to the
    existing one.  This will allow for ships to meet eachother.

    The only hook I can think of right now that would be necessary would be
    'at_object_receive'
    It's appropriate to apply to all objects not simply 'vessels'.
    '''
    pass


class DynamicRoom(SeaRoom):
    '''
    Probably all the action should take place here. That is the DSR is the only
    room that players should ever see.  So for instance the command sets should
    apply here etc.
    '''
    pass
