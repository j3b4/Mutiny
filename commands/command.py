"""
Commands

Commands describe the input the player can do to the game.

"""

from evennia import Command as BaseCommand
from evennia import default_cmds
import random


class Command(BaseCommand):
    """
    Inherit from this if you want to create your own
    command styles. Note that Evennia's default commands
    use MuxCommand instead (next in this module).

    Note that the class's `__doc__` string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    Each Command implements the following methods, called
    in this order:
        - at_pre_command(): If this returns True, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_command(): Extra actions, often things done after
            every command, like prompts.

    """
    # these need to be specified

    key = "MyCommand"
    aliases = []
    locks = "cmd:all()"
    help_category = "General"

    # optional
    # auto_help = False    #uncomment to deactive auto-help for this command.
    # arg_regex = r"\s.*?|$" #optional regex detailing how the part after
                           # the cmdname must look to match this command.

    # (we don't implement hook method access() here, you don't need to
    #  modify that unless you want to change how the lock system works
    #  (in that case see evennia.commands.command.Command))

    def at_pre_cmd(self):
        """
        This hook is called before `self.parse()` on all commands.
        """
        pass

    def parse(self):
        """
        This method is called by the `cmdhandler` once the command name
        has been identified. It creates a new set of member variables
        that can be later accessed from `self.func()` (see below).

        The following variables are available to us:
           # class variables:

           self.key - the name of this command ('mycommand')
           self.aliases - the aliases of this cmd ('mycmd','myc')
           self.locks - lock string for this command ("cmd:all()")
           self.help_category - overall category of command ("General")

           # added at run-time by `cmdhandler`:

           self.caller - the object calling this command
           self.cmdstring - the actual command name used to call this
                            (this allows you to know which alias was used,
                             for example)
           self.args - the raw input; everything following `self.cmdstring`.
           self.cmdset - the `cmdset` from which this command was picked. Not
                         often used (useful for commands like `help` or to
                         list all available commands etc).
           self.obj - the object on which this command was defined. It is often
                         the same as `self.caller`.
        """
        pass

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the `cmdhandler` right after `self.parser()` finishes, and so has access
        to all the variables defined therein.
        """
        self.caller.msg("Command called!")

    def at_post_cmd(self):
        """
        This hook is called after `self.func()`.
        """
        pass


class MuxCommand(default_cmds.MuxCommand):
    """
    This sets up the basis for Evennia's 'MUX-like' command style.
    The idea is that most other Mux-related commands should
    just inherit from this and don't have to implement parsing of
    their own unless they do something particularly advanced.

    A MUXCommand command understands the following possible syntax:

        name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]

    The `name[ with several words]` part is already dealt with by the
    `cmdhandler` at this point, and stored in `self.cmdname`. The rest is stored
    in `self.args`.

    The MuxCommand parser breaks `self.args` into its constituents and stores them
    in the following variables:
        self.switches = optional list of /switches (without the /).
        self.raw = This is the raw argument input, including switches.
        self.args = This is re-defined to be everything *except* the switches.
        self.lhs = Everything to the left of `=` (lhs:'left-hand side'). If
                     no `=` is found, this is identical to `self.args`.
        self.rhs: Everything to the right of `=` (rhs:'right-hand side').
                    If no `=` is found, this is `None`.
        self.lhslist - `self.lhs` split into a list by comma.
        self.rhslist - list of `self.rhs` split into a list by comma.
        self.arglist = list of space-separated args (including `=` if it exists).

    All args and list members are stripped of excess whitespace around the
    strings, but case is preserved.
    """

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the `cmdhandler` right after `self.parser()` finishes, and so has access
        to all the variables defined therein.
        """
        # this can be removed in your child class, it's just
        # printing the ingoing variables as a demo.
        super(MuxCommand, self).func()

#from evennia import Command #just fof clarity; already imported above

class CmdSetPower(Command):
    """
    Set the power of a character

    Usage:
        +setpower <1-10>

    This sets the power of the current character. This can only be
    used during character generation.
    """

    key = "+setpower"
    help_category = "mush"

    def func(self):
        "This performs the actual command."
        errmsg = "You must supply a number between 1 and 10"
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            power = int(self.args)
        except ValueError:
            self.caller.msg(errmsg)
            return
        if not (1 <= power <= 10):
            self.caller.msg(errmsg)
            return
        # at this point the argument is tested as valid. Let's set it.
        self.caller.db.power = power
        self.caller.msg("Your Power was set to %i." % power)

class CmdAttack(Command):
    """
    Issues an attack

    Usage:
        +attack

    This will calculate a new combat score based on your Power.
    Your combat score is visible to everyone in the same location.
    """

    key = "+attack"
    help_category = "mush"

    def func(self):
        "Calculate the random score between 1-10*Power"
        caller = self.caller
        power = caller.db.power
        if not power:
            # this can happen if caller is no of
            # our custom Character typeclass
            power = 1
        combat_score = random.randint(1, 10 * power)
            # interesting, I'm guessing random.randint takes two
            # arguments a from x to y range.  In this case the y
            # equals 10 times our power score. This produces a flat
            # curve
        caller.db.combat_score = combat_score

        # Announce
        message = "%s +attack%s with a combat score of %s!"
        caller.msg(message % ("You", "", combat_score))
        caller.location.msg_contents(message %
                                    (caller.key, "s", combat_score),
                                    exclude=caller)


from evennia import create_object

class CmdCreateNPC(Command):
    """
    Create a new npc

    Usage:
        +createNPC <name>

        Creates a new, named NPC. The NPC will start with a Power of 1
    """

    key = "+createnpc"
    aliases = ["+createNPC"]
    locks = "call:not perm(nonpcs)"
    help_category = "mush"

    def func(self):
        "creates the object and names it"
        caller = self.caller
        if not self.args:
            caller.msg("Usage: +createNPC <name>")
            return
        if not caller.location:
            # may not create npc when OOC
            caller.msg("You must have a location to create an NPC.")
            return
        # make name always start with a capital letter
        name = self.args.strip().capitalize()
        # create npc in caller's location
        npc = create_object("characters.Character",
                key=name,
                location=caller.location,
                locks="edit:id(%i) and perm(Builders)" % caller.id)
        #announce
        message = "%s created the NPC '%s'."
        caller.msg(message % ("You", name))
        caller.location.msg_contents(message % (caller.key, name),
                exclude=caller)


class CmdEditNPC(Command):
    """
    Edit an existing NPC.

    Usage:
        +editnpc <name>[/attribute> [= value]]

    Examples:
        +editnpc mynpc/power = 5
        +editnpc mynpc/power    - displays power value
        +editnpc mynpc          - shows all editable attributes
                                  and values

    This command edits an existing NPC. You must have permision
    to edit the NPC to use this.
    """
    key = "+editnpc"
    aliases = ["+editNPC"]
    locks = "cmd:not perm(nonpcs)"
    help_category = "mush"

    def parse(self):
        "We need to do some parsing here"
        args = self.args
        propname, propval = None, None
        if "=" in args:
            args, propval = [part.strip() for part in args.rsplit("=", 1)]
        if "/" in args:
            args, propname = [part.strip() for part in args.rsplit("/", 1)]
        # store, so we can access it below in func()
        self.name = args
        self.propname = propname
        # a propval without a propname is meaningless
        self.propval = propval if propname else None

    def func(self):
        "do the editing"

        allowed_propnames = ("power", "attribute1", "attribute2")

        caller = self.caller
        if not self.args or not self.name:
        # if not self.args or not self.key:  # try this
            caller.msg("Usage: +editnpc name[/propname][=propval]")
            return
        npc = caller.search(self.name)
        # npc = caller.search(self.key)  # as above see if key works instead of
        if not npc:
            return
        if not npc.access(caller, "edit"):
            caller.msg("You cannot edit this NPC.")
            return
        if not self.propname:
            # this means we just list available properties
            output = "Properties of %s:" % npc.key
            for propname in allowed_propnames:
                propvalue = npc.attributes.get(propname, default="N/A")
                output += "\n %s = %s" % (propname, propvalue)
            caller.msg(output)
        elif self.propname not in allowed_propnames:
            caller.msg("You may only change $s." %
                    ", ".join(allowed_propnames))
        elif self.propval:
            # assigning a new propvalue
            # in this example, the properties are all integers...
            intpropval = int(self.propval)
            npc.attributes.add(self.propname, intpropval)
            caller.msg("Set %s's  property '%s' to %s" %
                    (npc.key, self.propname, self.propval))
        else:
            # propname set, but not propval - show current value
            caller.msg("%s has property %s = %s" %
                    (npc.key, self.propname,
                        npc.attributes.get(propname, default="N/A")))

class CmdNPC(Command):
    """
    controls an NPC

    Usage: +npc <name> = <command>

    This causes the npc to perform a command as itself. It will do so 
    with its own permissions and accesses.
    """
    key = "+npc"
    aliases = ["+NPC"]
    locks = "call:not perm(nonpcs)"
    help_category = "mush"

    def parse(self):
        "Simple split of the = sign"
        name, cmdname = [part.strip()
                for part in self.args.rsplit("=", 1)]
        self.name, self.cmdname = name, cmdname

    def func(self):
        "Run the command"
        caller = self.caller
        if not self.cmdname:
            caller.msg("Usage: +npc <name> = <command>")
            return
        npc = caller.search(self.name)
        if not npc:
            return
        if not npc.access(caller, "edit"):
            caller.msg("You may not order this NPC to do anything.")
            return
        # send the command order
        npc.execute_cmd(self.cmdname, sessid=self.caller.sessid)
        caller.msg("You told %s to do '%s'." % (npc.key, self.cmdname))


from evennia import default_cmds    # imported above - this is a reminder
class CmdEcho(default_cmds.MuxCommand):
    """
    Simple command example

    Usage:
        echo <text>

    This command simply echoes text back to the caller.
    """

    key = "echo"
    aliases = ["frimble"]   # FYI "frimble" is a similar command on discworld
                            # mud
    locks = "cmd:all()"
    help_category = "Experimental"

    def func(self):
        "This actually does things"
        if not self.args:
            self.caller.msg("You didn't enter anything!")
        else:
            self.caller.msg("You hear an echo: '%s'" % self.args)
# last line
