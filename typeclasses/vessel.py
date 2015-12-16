# VESSELS - Boats etc.

from evennia import DefaultObject, search_object
from commands.vessel import CmdSetVessel
# from vesselscript import HoveToScript


class VesselObject(DefaultObject):

    def at_object_creation(self):
        # working on the sailing functions
        self.cmdset.add_default(CmdSetVessel)
        # not moving upon creation
        self.db.underway = False
        # The direction the boat is sailing East or West
        # 1 for West, -1 for East
        self.db.direction = 1
        # The rooms that the vessel will move through
        # #4 Eastern Shore; #5 Inlet Head;  #8 West Beach
        self.db.rooms = ["#4", "#5", "#8", ]
        # NEXT TODO: Work on navigation
        # self.scripts.add(HoveToScript)


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
        For acharacters, this runs the look command somehow
        I want to look at the room the vessel moves into and
        announce the view to the contents of the room.

        """
        self.msg_contents(self.at_look(self.location))
        # amazing this works perfectly!
        
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
        self.msg_contents("The %s gets underway." % self.key)

    def heave_to(self):
        # TODO: research other terms
        self.db.underway = False
        self.msg_contents("The %s heaves to at %s." % (self.key,
            self.location))

    def goto_next_room(self):
        # this might only make sense for the train track set up
        currentroom = self.location.dbref
        idx = self.db.rooms.index(currentroom) + self.db.direction
        # remember 1 = West and 2 = East

        if idx < 0 or idx >= len(self.db.rooms):
            # We've reached the end of the bay 
            self.heave_to()
            # reverse the direction of the vessel
            self.db.direction *= -1
        else:
            roomref = self.db.rooms[idx]
            room = search_object(roomref)[0]
            self.move_to(room)
            # above line redundant with look through on after_move



# last line
