# The Globe Rules
"""
Updating to implement the Haversone Formula
"""

import math
from haversine import haversine


def lookUp(position):
    "takes a position tuple and returns a dbref"
    if not type(position) == tuple:
        print "error: position needs to be a tuple"
        return
    else:
        "a position"


def measure(point_a, point_b):
    """
    Accepts two points defined by lat/long tuple  and returns the distance
    between them on the globe.

    I would like it too as well as the direction from a toward b.
    R = 6367 # Radius of the earth in km
        """
    distance = haversine(point_a, point_b)
    # the haversine module produces a result in KM
    # convert km to nautical miles
    return distance * 0.539957


def bearing(point_a, point_b):
    """
    Accepts two points and determines the initial heading
    required to begin a great circle trip to the second point.
    """
    pass


def travel(start_point, bearing, distance):
    """
    globe.travel accepts
    a starting point in lat/lon,
    a direction in 3 figure notation (0-360 degrees)
    and a distance in nautical miles
    It then returns a new point on the globe in lat/lon
    """
    asin = math.asin
    cos = math.cos
    sin = math.sin
    atan2 = math.atan2
    pi = math.pi

    lat1 = start_point[0]
    lon1 = start_point[1]
    # convert both to radians up front?
    lat1 = (pi / 180) * lat1
    lon1 = (pi / 180) * lon1

    debug = "pi = %s\n" % pi
    debug = debug + "start point: %s, %s\n" % (lat1, lon1)
    debug = debug + "bearing: %s\n" % bearing

    tc = (pi / 180) * bearing
    debug = debug + "bearing in radians: %s\n" % tc

    debug = debug + "distance: %s Nm\n" % distance
    d = (pi / (180*60)) * distance
    debug = debug + "distance in radians: %s\n" % d

    # requires point a is a tuple
    latr = asin(sin(lat1) * cos(d) + cos(lat1) * sin(d) * cos(tc))
    dlon = atan2(sin(tc) * sin(d) * cos(lat1), cos(d) - sin(lat1) * sin(latr))
    # lon = mod(lon1-dlon + pi, 2 * pi) - pi
    lonr = (lon1+dlon + pi) % (2 * pi) - pi
    debug = debug + "coordinates in radians: %s, %s\n" % (latr, lonr)

    lat = (180/pi) * latr
    lon = (180/pi) * lonr

    # rounding
    lat = int(lat)
    lon = int(lon)
    print debug

    destination = (lat, lon)
    print "Finished"
    return(destination)


def testGlobe():
    "Returns a message saying yes this is a globe object"
    return "Yes this is the globe.\n"


COMPASS_ROSE = [  # a list of directions and directions
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
    ("wsw", "west southwest", 225 + 45/2),
    ("w", "west", 270),
    ("wnw", "west northwest", 270 + 45/2),
    ("nw", "northwest", 315),
    ("nnw", "north northwest", 315 + 45/2)
    ]


# last line
