"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
# from evennia import create_script
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

    def at_object_leave(self, moved_obj, target_location):
        print "%s left" % moved_obj
        # if moved_obj was a vessel
        if not moved_obj.is_typeclass("typeclasses.vessel.VesselObject"):
            print "not a vessel though so no worries"
            return

        # then search contents of room for any other vessels
        print "Remaining objects: "
        # print self.contents
        vessel_count = 0
        for floater in self.contents:
            print floater
            if floater.is_typeclass("typeclasses.vessel.VesselObject"):
                vessel_count = vessel_count + 1
        print "vessel count = %s" % vessel_count
        # if any vessels remain, then return
        if vessel_count > 1:
            return
        else:
            # if none, then add the script
            self.scripts.add("typeclasses.scripts.CleanSeaRoom")

    def at_object_receive(self, moved_obj, source_location):
        print "%s has arrived from %s" % (moved_obj, source_location)
        if self.scripts.get("CleanUp"):
            if not moved_obj.is_typeclass("typeclasses.vessel.VesselObject"):
                print "not a vessel though so no worries"
                return
            else:
                print "A vessel arrived so stop the cleanup"
                self.scripts.delete("CleanUp")
        else:
            print "CleanUp wasn't running so no worries."

        '''
    def SelfClean(self):
        print "Self cleaning."
        if self.contents:
            print "First move all objects to limbo"
            for floater in self.contents:
                clean = floater.move_to("#2")  # #2 is limbo for now
                if not clean:
                    print "Failed to clean out %s" % floater
                    break
        self.delete()
        '''


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
