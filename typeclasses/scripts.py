"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

from evennia import DefaultScript


class Script(DefaultScript):
    """
    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there
                  is actual combat going on).
      at_start() - Called every time the script is started, which for
                  persistent scripts is at least once every server start. Note
                  that this is unaffected by self.delay_start, which only
                  delays the first call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True,
                  which will delay the first call of this method by
                  self.interval seconds. If self.interval==0, this method will
                  never be called.
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned
                  False.  at_server_reload() - Called when server reloads. Can
                  be used to save temporary variables you want should survive a
                  reload.
      at_server_shutdown() - called at a full server shutdown.

    """
    pass


class CleanSeaRoom(Script):
    """
    The CleanSeaRoom Script is added to every new dynamic sea room upon
    creation and fires when the last vessel object leaves the room. It then
    starts a timer. If no new vessel arrives in the room before the timer
    expires then all flotsam (floating objects) in the room are moved to an
    arbitrary room and the room itself is deleted.

    Not using it for now. Maybe it's totally unneccesary.
    """

    def at_script_creation(self):
        self.key = "CleanUp"
        self.interval = 20
        self.repeats = 1
        self.start_delay = True
        print "%s will delete %s in %s seconds" % (self.key,
                                                   self.obj.dbref,
                                                   self.interval)

    def at_repeat(self):
        print "%s secs later. Time to clean up. Unlesss..." % self.interval
        self.obj.delete()
        # self.obj.SelfClean()


class VesselMove(Script):
    def at_script_creation(self):
        self.key = "vesselmove"
        self.interval = 3
        self.persisent = True
        self.repeats = 48  # two days non-stop
        self.start_delay = 5
        self.time = 0

    def at_repeat(self):
        self.obj.update_position()
        self.time += 1

    def at_stop(self):
        time = str(self.time)
        string = "After %s hours of rowing you stop."
        self.obj.msg_contents(string % time)
        self.obj.db.underway = False
        self.obj.db.speed = 0  # not moving anymore
        self.obj.msg_contents("The %s heaves to at %s." % (self.obj.key,
                              self.obj.location))


class WorldWind(Script):
    '''
    This script is an in game object that stores the current wind speed and
    direction.  Presently one wind for the whole world.
    One purpose of this script is to allow me to change the wind in game to
    test other physics.
    The plan is to create a single script from this typeclass at_initial_setup
    '''

    def at_script_creation(self):
        self.key = "WorldWind"
        self.desc = "stores the current wind speed and direction"
        self.db.wind = (90.0, 3.3)  # direction, speed
        self.db.current = (0.0, 0.0)  # direction, speed
        self.interval = 0
        self.persistent = True

    def return_wind(self, position):
        return self.db.wind

    def return_current(self, position):
        return self.db.wind

    def set_wind(self, direction, speed):
        self.db.wind = (float(direction), float(speed))

    def set_current(self, direction, speed):
        self.db.current = (float(direction), float(speed))
# Last Line
