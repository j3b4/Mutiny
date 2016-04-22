# The Globe Rules
"""
Updating to implement the Haversone Formula
Moving the code that allows a vessel to arrive somwhere here from the original
Vessel command "North"  so that it can be used in other movement commands.
"""

import math
# from random import choice, randint
from LatLon23 import LatLon  # , Latitude, Longitude, string2latlon
from evennia.utils import search, inherits_from
from evennia.utils.create import create_object


def travel(start_point, heading, distance):
    """
    accepts a starting point in lat lon
    determines destination after travelling a certain distance for
    a particular start heading
    """
    distance = distance * 1.852  # convert NM to KM
    # print "**********\ndebugging travel\n*********"
    # print "Checking on the start_point"
    # print start_point
    #  print type(start_point)
    lat1 = start_point[0]
    lon1 = start_point[1]
    origin = LatLon(lat1, lon1)
    destination_obj = origin.offset(heading, distance)
    destination_tup = destination_obj.to_string()
    lat2 = round(float(destination_tup[0]), 2)
    lon2 = round(float(destination_tup[1]), 2)
    # print "Destination string: "
    # print lat2
    # print lon2
    # print "**********\nend debugging travel\n*********"
    return((lat2, lon2))


def arrive_at(vessel, position):
    '''
    # The following code moves a vessel to a new position and room that
    # matches that position.
    # ARRIVE AT

    # Look up room then move to it or create it and move to it
    '''

    # Check the arguments to make sure vessel is a vessel and
    # position is a position

    # Look up room in teh entier DB
    if position:
        room = search.search_object_attribute(key="coordinates",
                                              value=position)
    else:
        string = "position: %s" % str(position)
        vessel.msg_contents(string)
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


def measure(point_a, point_b):
    pass


def world_wind(position):
    '''
    Call this to ask what is the wind at position
    Returns a direction and a speed

    This working copy just picks two values at random. This will make for
    dramatic wind shifts.
    '''
    """
    direction = choice(COMPASS_ROSE)
    # COMPASS_ROSE contains three values
    speed = randint(0, 65)
    return (float(direction[2]), float(speed))
    """
    # provisional sane fixed wind
    return (0.0, 45.0)  # 90 knots out of the south


def current_current(position):
    '''
    Returns the current current at position.
    '''
    """
    direction = choice(COMPASS_ROSE)
    speed = randint(0, 12)  # current speed
    return (float(direction[2]), float(speed))
    """
    return (90.0, 45.0)  # 90  knots westerly current


def resultant((dir1, mag1), (dir2, mag2)):
    '''
    resultant() adds one polar vector to another.
    use this as often as needed to add all forces acting on a floating object.
    '''
    # Convert both angles to radians
    dir1 = math.radians(dir1)
    dir2 = math.radians(dir2)
    x = math.sin(dir1) * mag1 + math.sin(dir2) * mag2
    y = math.cos(dir1) * mag1 + math.cos(dir2) * mag2
    mag_result = math.hypot(x, y)
    print "\nhypontenuse: %s" % mag_result
    dir_rad = math.atan2(y, x)
    print "direction radians: %s\n" % dir_rad
    # dir_deg = dir_rad * (180/math.pi)  # conversion
    dir_deg = math.degrees(dir_rad)  # convert radians to degress
    print "direction degrees: %s\n" % dir_deg
    return (dir_deg, mag_result)


def actual_course(position, heading, power):
    '''
    Calculate the vessels actual course if position, power, and heading are
    known. Use "position" to get local wind and current.  Then add to the power
    vector using the resultant function above.
    '''
    ship_power = (float(heading), float(power))
    wind = world_wind(position)
    current = current_current(position)
    natural_forces = resultant(wind, current)
    print "natural forces = %s" % str(natural_forces)
    print "\n\n   * adding power vector *"
    print "power = %s" % str(ship_power)
    actual_course = resultant(natural_forces, ship_power)
    print "actual course = %s" % str(actual_course)
    new_position = travel(position, actual_course[0], actual_course[1])
    print "new position = %s" % str(new_position)
    return new_position


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
