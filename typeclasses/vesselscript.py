# Scripts for the vessel object
# First up: A coastal cruise around the bay

from evennia import DefaultScript

class HoveToScript(DefaultScript):
    # based on Tutorial TrainStoppedScript
    """
    This manages the delay while the vessel lingers in 
    a particular coastal room.  

    This is not quite what we want since it would be preferable to describe
    the movement, underway, of a vessel through the coastal waters.

    So thats on the todo list.
    """

    def at_script_creation(self):
        self.key = "hove_to"
        # no real idea what any of the next properties really mean
        self.interval = 60
        # sets a delay property of 30 secs on this script?
        self.persistent = True
        # not sure what this is.
        self.repeats = 1
        # not sure either
        self.start_delay = True

    def at_repeat(self):
        self.obj.get_underway()

    def at_stop(self):
        self.obj.scripts.add(UnderwayScript)


class UnderwayScript(DefaultScript):
    # changed above from "(Script)" since I think that must have been a legacy
    # error in the tutorial

    def at_script_creation(self):
        self.key = "underway"
        self.interval = 60
        self.persistent = True

    def is_valid(self):
        # determines if the script should still be running or not.
        return self.obj.db.underway
        # So if the object is "underway" then the UnderwayScript should
        # still be running.  Fine.

    def at_repeat(self):
        if not self.obj.db.underway:
            self.stop()
        else:
            self.obj.goto_next_room()

    def at_stop(self):
        self.obj.scripts.add(HoveToScript)

"""
These scripts work as state system: when the vessel is stopped (hove to), 
it waits for 30 secs then gets underway again. When underway, it moves to the 
next room every second. The vessel is always in one of those two states - both 
scripts take care of adding the other one once they are done.

"""

# Last Line
