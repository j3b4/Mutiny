# VESSELS - Boats etc.

from evennia import DefaultObject  # , search_object
from commands.vessel import CmdSetVessel, CmdSetOnboard, CmdSetConn
# from evennia import utils
from world.globe import travel
# from vesselscript import HoveToScript


class VesselObject(DefaultObject):

    def at_object_creation(self):
        # working on the sailing functions
        self.cmdset.add_default(CmdSetVessel)
        # not moving upon creation
        # self.db.underway = False
        # The direction the boat is sailing East or West
        self.db.testing = True
        self.permissions.add("vessel")

# attempt full overload of announce_move_from
    def announce_move_from(self, destination):
        """
        Called if the move is to be announced. This is
        called while we are still standing in the old
        location.
        Args:
            destination (Object): The place we are going to.
        """
        if not self.location:
            return
        name = self.name
        loc_name = ""
        loc_name = self.location.name
        dest_name = destination.name
        string = "The %s is leaving %s, cruising towads %s."
        self.location.msg_contents(string % (name, loc_name, dest_name),
                                   exclude=self)

    def announce_move_to(self, source_location):
        """
        Called after the move if the move was not quiet. At this point
        we are standing in the new location.
        Args:
            source_location (Object): The place we came from
        """

        name = self.name
        if not source_location and self.location.has_player:
            # This was created from nowhere and added to a player's
            # inventory; it's probably the result of a create command.
            string = "You now have %s in your possession." % name
            self.location.msg(string)
            return

        src_name = "nowhere"
        loc_name = self.location.name
        if source_location:
            src_name = source_location.name
        string = "The %s arrives at %s, cruising in from %s."
        self.location.msg_contents(string % (name, loc_name, src_name),
                                   exclude=self)

    def at_after_move(self, source_location):
        """
        For characters, this runs the look command somehow
        I want to look at the room the vessel moves into and
        announce the view to the contents of the room.

        """
        self.msg_contents(self.at_look(self.location))

    def at_object_receive(self, moved_obj, source_location):
        if moved_obj.is_typeclass("characters.Character"):
            # only pc or npcs can have these commands
            moved_obj.cmdset.add(CmdSetOnboard, permanent=True)
            print "Adding Onboard commands to %s" % moved_obj

    def at_object_leave(self, moved_obj, target_location):
        moved_obj.cmdset.delete(CmdSetOnboard)
        print "Deleting Onboard commands from %s" % moved_obj
        moved_obj.cmdset.delete(CmdSetConn)
        print "Deleting Conning commands from %s" % moved_obj

# end of overload attempt.
    def return_view(self):
        """
        This should let the view outsite become part of the view
        inside a vessel object.

        If the vessel has "below decks" or "cabin" type rooms. This would have
        to be restricted.
        """
        view = self.at_look(self.location)
        return view

    def get_underway(self):
        self.db.underway = True
        self.db.speed = 60  # speed is in knots aka nautical miles/hour
        self.msg_contents("The %s gets underway." % self.key)

    def heave_to(self):
        # TODO: research other terms
        self.db.underway = False
        self.db.speed = 0  # not moving anymore
        self.msg_contents("The %s heaves to at %s." % (self.key,
                          self.location))

    def steer_to(self, heading):
        '''
        This changes the objects heading
        I guess this is called by a players command. Not sure whether it makes
        sense here.
        '''
        self.db.bearing = heading
        string = "The %s steers to %s degrees"
        self.msg_contents(string % (self.key, heading))

    def update_position(self):
        '''
        This function updates the ships position after obtaining the time from
        a script maybe?
        after collecting information
        # def travel(start_point, bearing, distance):
        '''
        old_pos = self.db.position
        bearing = self.db.bearing
        speed = self.db.speed

        new_pos = travel(old_pos, bearing, speed)
        # coordinates = str(new_pos)
        self.db.position = new_pos
        string = "The vessel moves %s knots heading %s"
        string + " and arrives at %s."
        self.msg_contents(string)  # % (str(speed), str(bearing), coordinates))
        """
        Assume that each travel interval is 1 hour, distance will be equal to
        speed in knots
        """

# last line
