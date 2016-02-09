"""
Globe

Starting with a copy of the script typeclass. I'm going to try to create
a "globe" consisiting of a dictionary of coordinates and room db refs.

The idea is that any location at sea should be implemented by linking to a room

It might also be possible to develop other properties of the globe such as
currents and weather and climate patterns.  I'm not sure.

"""

from evennia import DefaultScript


class Globe(DefaultScript):
    """
    * available properties
     desc (string)      - optional description of script, shown in listings
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    """
    key = "globe"
    name = "globe"
    desc = "a map of the world"
    persistent = True
    """
    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    """
    atlas = {(6, 4): '#8',
             (6, 5): '#41',
             (7, 3): '#5',
             (8, 4): '#4',
             }

    style = "round"

    def lookUp(position, atlas):
        "takes a position tuple and returns a dbref"
        if not type(position) == tuple:
            print "position needs to be a tuple"
            return
        else:
            return atlas[position]

    def testGlobe():
        "Returns a message saying yes this is a globe object"
        return "Yes this is the globe.\n"

# last line
