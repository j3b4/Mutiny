"""
Portage Command Sets
based on the tutorial at
https://github.com/evennia/evennia/wiki/Adding%20Command%20Tutorial

"""
from evennia import CmdSet
# from commands.command import CmdEcho
# above example that worked
from commands.mutinous import CmdSwear
# from commands import mutinous

class PortageCmdSet(CmdSet):

    key = "PortageCmdSet"

    def at_cmdset_creation(self):
        self.add(CmdSwear())
# last line
