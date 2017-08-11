# VESSELS - Boats etc.

import math
from evennia import DefaultObject
from evennia.utils import search, inherits_from
from evennia.utils.create import create_object
from commands.vessel import CmdSetVessel, CmdSetConn
from commands.vessel import CmdSetOnDeck
# from evennia import utils
from world.globe import add_vector, move_vector, get_weather
from evennia import TICKER_HANDLER as tickerhandler


class FloatingObject(DefaultObject):
    '''
    The floating object as a base for vessels etc.
    Floating objects can be adrift or anchored. If adrift, they will move every
    tick.
    '''
    def at_object_creation(self):
        self.cast_off()
        self.db.windage = 0.1  # default windage

    def cast_off(self):
        '''
        When cast_off, a vessel is subject to movement forces. Current, wind,
        and even self power like oars. This means a script will start to run
        updating position constantly based on those forces.
        '''
        self.db.adrift = True
        self.msg_contents("The %s is now adrift." % self.key)
        tickerhandler.add(3, self.make_way, idstring="adrift")
        # updates postion

    def anchor(self):
        tickerhandler.remove(3, self.make_way, idstring="adrift")
        self.db.power = 0
        self.db.underway = False
        self.db.adrift = False

    def make_way(self):
        '''
        move in response to impelling forces:
        wind, current, and power
        on a bare floating object this is purely based on wind and current
        a floater doesn't have a heading and never has power.
        '''
        # Could get wind and current here
        (wind, current) = get_weather(self.db.position)
        print "wind: %s" % str(wind)
        print "current: %s" % str(current)
        # then calculate actual course here.
        wind[1] = wind[1] * self.windage  # reduces wind effect to a fraction
        course = add_vector(wind, current)
        position = move_vector(self.db.position, course)
        self.arrive_at(position)

    def arrive_at(self, position):
        '''
        # The following code moves an object to a new position and room that
        # matches that position.
        '''
        vessel = self

        # Check the arguments to make sure vessel is a vessel and
        # position is a position

        # Look up room in teh entier DB
        if position:
            room = search.search_object_attribute(key="coordinates",
                                                  value=position)
        else:
            string = "position: %s" % str(position)
            self.msg_contents(string)
            return
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
            # but if not dry land
            # ... lets get on with it and move
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

        def make_way(self, course):
            old_position = self.db.position
            position = move_vector(old_position, course)
            self.msg_contents("New position = %s" % str(position))
            self.arrive_at(self, position)

        def at_tick(self):
            '''
            All floating objects move every tick unless anchored/moored.
            So at tick, we calculate course and make_way
            '''
            pass

    def at_tick(self):
        self.make_way()


class VesselObject(FloatingObject):
    '''
    This is for floating objects that can be boarded steered and controlled
    so we'll inherit the basic properties of a floating object and then add
    boarding functions, control stations, and the power and sail functions
    '''
    def at_object_creation(self):
        self.cmdset.add_default(CmdSetVessel)
        self.db.underway = False
        self.db.heading = 0
        self.permissions.add("vessel")

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
            moved_obj.cmdset.add(CmdSetOnDeck, permanent=True)
            print "Adding OnDeck commands to %s" % moved_obj

    def at_object_leave(self, moved_obj, target_location):
        moved_obj.cmdset.delete(CmdSetOnDeck)
        print "Deleting OnDeckcommands from %s" % moved_obj
        moved_obj.cmdset.delete(CmdSetConn)
        print "Deleting Conning commands from %s" % moved_obj

    def return_view(self):
        """
        This should let the view outsite become part of the view
        inside a vessel object.

        If the vessel has "below decks" or "cabin" type rooms. This would have
        to be restricted.
        """
        view = self.at_look(self.location)
        return view
        # Honestly I don't think this does anything.

    def steer_to(self, heading):
        '''
        This changes the objects heading
        I guess this is called by a players command. Not sure whether it makes
        sense here.
        '''
        self.db.heading = float(heading)
        string = "The %s steers to %s degrees"
        self.msg_contents(string % (self.key, heading))

    def get_underway(self, power):
        '''
        Get going, rowing maybe?
        '''
        self.db.power = float(power)
        self.db.underway = True
        if not self.db.adrift:
            self.cast_off()

    def make_way(self):  # over ride the floating objects make_way
        '''
        move in response to impelling forces:
        wind, current, and power
        '''
        # Could get wind and current here
        (wind, current) = get_weather(self.db.position)
        power = self.db.power
        sails = self.db.sails
        # polar = self.db.polar  # set by spawner?
        heading = float(self.db.heading)
        bearing = (heading, power)
        print "wind: %s" % str(wind)
        print "current: %s" % str(current)
        # then calculate actual course here.
        if sails:
            self.msg_contents("You're sailing")
            wind = (heading, wind[1]/2)
            # this lets us sail at any wind angle at half windspeed
        else:
            '''
            if no sails, then wind exerts a fraction of its power
            on the floating object based on the vessel's windage
            '''
            wind = (wind[0], wind[1] * self.db.windage)
            # reduces wind effect to a fraction
        course = add_vector(wind, current)
        if power:
            print "power: %s" % str(power)
            print "bearing: %s" % str(bearing)
            course = add_vector(course, bearing)
            print "course: %s" % str(course)
        position = move_vector(self.db.position, course)
        self.arrive_at(position)

    def sail(self, wind, heading):
        # TODO: seriously consider moving this to a sailing module.
        '''
        take wind (direction & speed) and boats heading.
        then calculate true wind angle TWA
        then look TWA and wind speed WS up in the polare
        interpolate if necessary
        return the boat speed and course over water.
        '''
        print "sailing attempted"

        # calculate TWA
        wind_direction = wind[0]
        twa = math.copysign(wind_direction - heading, 1)
        if twa > 180:
            twa = 2 * 180 - twa

        # lookup polar
        polar = self.db.polar
        print "polar name = %s" % polar
        # get find the bounding box of 1 to 4 windspeed and twa values
        # interpolate
        # return a boat speed and heading (should be same heading)

    def set_boarding_area(self, station):
        '''
        This method designates one of the vessel's stations to be the default
        arrival location for characters using the "board" command from outside
        the vessel.
        '''
        self.db.boarding_area = station


class ShipStation(DefaultObject):
    '''
    ShipStations are parts of a large vessel. Stations can be rooms or objects
    all must be attached or contained by a master VesselObject
    The station must relay information between the Vessel and its own contents.
    '''

    def at_object_creation(self):
        '''
        At creation, define the master vessel - this is immutable since a
        station must be a part of a certain ship.
        '''
        pass

    def at_msg_receive(self, text):
        '''
        When the vessel messages contents, this station decides whether to
        relay anything to its own contents -ie. players or NPCs.
        '''
        self.msg_contents(text)
        pass

    ###
    # Below I've copied the command setting functions from the vessel object.
    # But this will not be satisfactory. Well, perhaps I can divy up command
    # sets to different parts of the vessel. That actually makes some sense
    # since command sets very specidificaly defines most ShipStations.
    # So, some ship station typeclasses will have built in comman sets, others
    # can be customuized.
    # but as for the custom look?  Yeah I can tweak it.


class OnDeck(ShipStation):
    '''
    OnDeck is a high level ShipStation that includes all stations which have a
    full exterior view, potentially allow debarking and boarding. Are exposed
    to weather. I'm not sure what other features.
    '''
    def at_object_creation(self):
        ''' add '''
        self.cmdset.add_default(CmdSetOnDeck)

    def at_object_leave(self, moved_obj, target_location):
        moved_obj.cmdset.delete(CmdSetOnDeck)
        print "Deleting OnDeckcommands from %s" % moved_obj
        moved_obj.cmdset.delete(CmdSetConn)
        print "Deleting Conning commands from %s" % moved_obj

# last line
