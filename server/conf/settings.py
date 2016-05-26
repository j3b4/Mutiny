"""
Evennia settings file.

The available options are found in the default settings file found
here:

/home/aeon/Evennia/evennia/evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Portage"

######################################################################
# Django web features
######################################################################


# The secret key is randomly seeded upon creation. It is used to sign
# Django's cookies. Do not share this with anyone. Changing it will
# log out all active web browsing sessions. Game web client sessions
# may survive.
# SECRET_KEY = 'CIW/j3-!_4xY7@uG"fmsd*g[AzJ2LM#kEy<(~91h'
SECRET_KEY = '?/,yM-S9rnbqTjR"c7Z:CB#"@AIak^HusQ(;g`&N'

#####################################################################
# Contrib config                                                    #
#####################################################################
GAME_INDEX_LISTING = {
        'game_status': 'pre-alpha',
        'game_website': 'http://j3b.mdns.org:8000/',
        'listing_contact': 'j3b@3b1.org',
        'telnet_hostname': 'j3b.mdns.org',
        'telnet_port': 4000,
        'short_description': 'Horatio Hornblower meets Dwarf Fortress',
        'long_description': '''
Horatio Hornblower is a fictional
Napoleonic Wars era Royal Navy officer who is the protagonist
of a series of novels by C. S. Forester. He was later the
subject of films and radio and television programs..... Dwarf
Fortress (officially called Slaves to Armok: God of Blood
Chapter II: Dwarf Fortress) is a part construction and
management simulation, part roguelike, indie video game
created by Tarn and Zach Adams.
'''
                }


