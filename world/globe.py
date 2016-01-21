# this is just a module I guess.
atlas = {(6, 4): '#8',
         (6, 5): '#41',
         (7, 3): '#5',
         (8, 4): '#4',
         }

style = "round"


def lookUp(position):
    "takes a position tuple and returns a dbref"
    if not type(position) == tuple:
        print "error: position needs to be a tuple"
        return
    else:
        return atlas[position]


def testGlobe():
    "Returns a message saying yes this is a globe object"
    return "Yes this is the globe.\n"

# last line
