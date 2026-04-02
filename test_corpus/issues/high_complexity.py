
def complex_decision(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return "A"
            elif z < 0:
                return "B"
            else:
                return "C"
        elif y < 0:
            return "D"
        else:
            if z > 0:
                return "E"
            return "F"
    elif x < 0:
        return "G"
    else:
        return "H"
