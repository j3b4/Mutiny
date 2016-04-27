# The Globe Rules
"""
Updating to implement the Haversone Formula
Moving the code that allows a vessel to arrive somwhere here from the original
Vessel command "North"  so that it can be used in other movement commands.
"""

import math
# from random import choice, randint
from LatLon23 import LatLon  # ,Latitude, Longitude, string2latlon
from evennia.utils import search  # ,inherits_from
# from evennia.utils import create, search


def move_vector(fix, vector):
    """
    accepts a starting fix in lat lon
    determines destination after travelling a certain distance for
    a particular start heading
    """
    distance = vector[1] * 1.852  # convert NM to KM
    heading = vector[0]  # is this radians or degrees?
    # print "**********\ndebugging travel\n*********"
    # print "Checking on the start_point"
    # print start_point
    # print type(start_point)
    lat1 = fix[0]
    lon1 = fix[1]
    origin = LatLon(lat1, lon1)
    destination_obj = origin.offset(heading, distance)
    destination_tup = destination_obj.to_string()
    lat2 = round(float(destination_tup[0]), 2)
    lon2 = round(float(destination_tup[1]), 2)
    return((lat2, lon2))


def get_weather(position):
    '''
    return the wind and current
    '''
    matches = search.search_script("WorldWind")
    print "\nmatches = %s, type = %s" % (matches, type(matches))
    if not matches:
        print "No match in the db for WorldWind.\n"
        return
    WorldWind = matches[0]
    string = "wind is %s\ncurrent is %s"
    wind = WorldWind.return_wind((1, 1))
    current = WorldWind.return_current((1, 1))
    print string % (str(wind), str(current))
    return (wind, current)


def measure(point_a, point_b):
    pass


def current_current(position):
    '''
    Returns the current current at position.
    '''
    """
    direction = choice(COMPASS_ROSE)
    speed = randint(0, 12)  # current speed
    return (float(direction[2]), float(speed))
    """
    # return (0.0, 0.0)  # 90  knots westerly current
    pass


def add_vector(v1, v2):
    '''
    resultant() adds one polar vector to another.
    use this as often as needed to add all forces acting on a floating object.
    It returns a new vector to the caller

    v1 and v2 should be in the form (degree, nautical miles)
    '''
    # Convert both angles to radians
    # check input

    print "v1 = %s" % str(v1)
    print "v2 = %s" % str(v2)
    dir1 = math.radians(v1[0])
    dir2 = math.radians(v2[0])
    mag1 = v1[1]
    mag2 = v2[1]
    # Test: simple reve. x and y once.
    y = math.sin(dir1) * mag1 + math.sin(dir2) * mag2
    x = math.cos(dir1) * mag1 + math.cos(dir2) * mag2
    mag_result = math.hypot(x, y)
    print "\nhypontenuse: %s" % mag_result
    dir_rad = math.atan2(y, x)
    # print "direction radians: %s\n" % dir_rad
    # dir_deg = dir_rad * (180/math.pi)  # conversion
    dir_deg = math.degrees(dir_rad)  # convert radians to degress
    print "direction degrees: %s\n" % dir_deg
    return (dir_deg, mag_result)


COMPASS_ROSE = [  # a list of directions and directions
    # TODO add these to the "Steer" command
    # and add a heading and bearing command
    ("n", "north", 0),
    ("nne", "north northeast", 45/2),
    ("ne", "northeast", 45),
    ("ene", "east northeast", (45 + 45/2)),
    ("e", "east", 90),
    ("ese", "east southeast", (90 + 45/2)),
    ("se", "southeast", 135),
    ("sse", "south southeast", (135 + 45/2)),
    ("s", "south", 180),
    ("ssw", "south southwest", (180 + 45/2)),
    ("sw", "southwest", 225),
    ("wsw", "west southwest", (225 + 45/2)),
    ("w", "west", 270),
    ("wnw", "west northwest", (270 + 45/2)),
    ("nw", "northwest", 315),
    ("nnw", "north northwest", (315 + 45/2))
    ]


# last line
