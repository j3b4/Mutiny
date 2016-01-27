"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit


class Exit(DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use
                        `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and
                               should rebuild the Exit cmdset along with a
                               command matching the name of the Exit object.
                               Conventionally, a kwarg `force_init` should
                               force a rebuild of the cmdset, this is triggered
                               by the `@alias` command when aliases are
                               changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an attribute
                            `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_before_traverse(traveller) - called just before traversing.
        at_after_traverse(traveller, source_loc) - called just after
                                                   traversing.
        at_failed_traverse(traveller) - called if traversal failed for some
                                        reason. Will not be called if the
                                        attribute `err_traverse` is defined, in
                                        which case that will simply be echoed.
    """
    def at_object_creation(self):
        # hiding this in case it can be solved by simply prioritising vessel
        # navigation commands over exits.
        self.locks.add("traverse: NOT perm(vessel)")
        # self.db.err_traverse = "Dry land!"
        # TODO: echo this to vessel contents.
        # probably best to simply build vessels to echo all msgs they receive.
        # vessels cannot use normal default exits.

    def at_failed_traverse(exit, vessel):
        # Tell the occupants of a vessel why move through exit failed.
        vessel.msg_contents("The %s cannot sail on to dry land" % vessel)
        print "This is where I would put a message to the boat"
        print "exit = %s" % exit
        print "vessel = %s" % vessel
