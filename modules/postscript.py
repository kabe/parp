#!/usr/bin/env python


# Postscript module

# Newline code
NL = "\n"
# Dimension of the draw space
DATA_DIMENSION = 2
# Font name
FONT_NAME = "Times-Roman"
# Font size
FONT_SIZE = 4

# Exception class
class PostScriptException(Exception):
    """Exception class for error in generating Postscript.
    """
    pass


class Position(object):
    """Position class
    """

    def _get_x(self):
        return self._x

    x = property(_get_x)

    def _get_y(self):
        return self._y

    y = property(_get_y)

    def __init__(self, *xs, **kwarg):
        """Initializer.

        @param *xs initial coordinates
        @param **kwarg initial coordinates
        """
        self._xs = xs
        if len(xs) != DATA_DIMENSION:
            raise PostScriptException(
                "Dimension does not match: %s" % (str(xs)))
        if xs:
            self._x = xs[0]
            self._y = xs[1]
        else:
            self._x = kwarg["x"]
            self._y = kwarg["y"]


def begin():
    """
    """
    l = []
    l.append("%!PS")
    #l.append("")
    #l.append("%%BoundingBox 0 0 2000 3000")
    return l


def finalize():
    """
    """
    l = []
    l.append("showpage")
    return l


def draw_rect_position(x0, x1, *args):
    """Draw a rectangle by position

    @param x0 left-bottom position
    @param x1 right-top position
    @param *args
    """
    l = []
    GRAYSACLE = 0.9
    xsize = x1.x - x0.x
    ysize = x1.y - x0.y
    l.append("%% RECTANGLE")
    l.append("gsave")
    l.append("    0 0 0 1 setcmykcolor")
    l.append("    0.1 setlinewidth")
    l.append("    %f %f moveto" % (x0.x, x0.y))
    l.append("    %f %f rlineto" % (xsize, 0))
    l.append("    %f %f rlineto" % (0, ysize))
    l.append("    %f %f rlineto" % (-xsize, 0))
    l.append("    %f %f rlineto" % (0, -ysize))
    l.append("    closepath")
    l.append("    gsave")
    if args:
        colour = args[0]
        l.append("        %f %f %f %f setcmykcolor" % (
                colour[0], colour[1], colour[2], colour[3]))
    else:
        l.append("        %f setgray" % (GRAYSACLE,))
    l.append("        fill")
    l.append("    grestore")
    l.append("    stroke")
    l.append("grestore")
    return l


def draw_rect_size(x0, size, *args):
    """Draw a rectangle by size

    @param x0 left-bottom position
    @param size Position object for size
    @param *args
    """
    return draw_rect_position(
        x0,
        Position(x0.x + size.x, x0.y + size.y),
        *args)


def draw_axis(x0, x1):
    """Draw axis line.

    @param x0
    @param x1
    """
    l = []
    l.append("% AXIS")
    l.append("gsave")
    l.append("    0 0 0 1 setcmykcolor")
    l.append("    newpath")
    l.append("    %f %f moveto" % (x0.x, x0.y))
    l.append("    %f %f lineto" % (x1.x, x0.y))
    l.append("    %f %f moveto" % (x0.x, x0.y))
    l.append("    %f %f lineto" % (x0.x, x1.y))
    l.append("    stroke")
    l.append("grestore")
    return l


def place_grid(x, y):
    """Draw axis line.

    @param x
    @param y
    """
    l = []
    l.append("% GRID")
    l.append("gsave")
    l.append("    0 0 0 1 setcmykcolor")
    l.append("    0.1 setlinewidth")
    l.append("    newpath")
    l.append("    %f %f moveto" % (0, 0))
    l.append("    %f %f rlineto" % (x, 0))
    l.append("    %f %f rlineto" % (0, y))
    l.append("    %f %f rlineto" % (-x, 0))
    l.append("    %f %f rlineto" % (0, -y))
    l.append("    closepath")
    l.append("    stroke")
    l.append("grestore")
    return l


def _place_text(text, position):
    """Place a text(wrapped. use place_text(.)).

    @param text string to place
    @param position position to place (specify left bottom)
    """
    l = []
    l.append("%% Place \"%s\"" % (text,))
    l.append("gsave")
    l.append("    0 0 0 1 setcmykcolor")
    l.append("    /%s findfont" % (FONT_NAME,))
    l.append("    %d scalefont setfont" % (FONT_SIZE,))
    l.append("    %f %f moveto" % (position.x, position.y))
    l.append("    (%s) show" % (text))
    l.append("grestore")
    return l


def place_text(text, position):
    """Place a text.

    @param text string to place
    @param position position to place (specify left bottom)
    """
    l = _place_text(text, position)
    return l


def place_colourlegend(colourdic, x0, size):
    """Place colours legend.

    @param colourdic dictionary from text to cmykcolour tuple
    @param x0 left-bottom position of the legend
    @param size size of legend
    """
    l = []
    apps = colourdic.keys()
    # Draw Box
    l.append("%% Colour Legend")
    l.append("gsave")
    l.append("    0 0 0 1 setcmykcolor")
    l.append("    0.1 setlinewidth")
    l.append("    newpath")
    l.append("    %d %d moveto" % (x0.x, x0.y))
    l.append("    %d %d rlineto" % (size.x, 0))
    l.append("    %d %d rlineto" % (0, size.y))
    l.append("    %d %d rlineto" % (-size.x, 0))
    l.append("    %d %d rlineto" % (0, -size.y))
    l.append("    closepath")
    l.append("    stroke")
    l.append("grestore")
    distance_between_colour = size.y / len(colourdic)
    csize = Position(size.x, distance_between_colour)
    for idx, app in enumerate(colourdic):
        position_lb = Position(x0.x, x0.y + idx * distance_between_colour)
        colour = colourdic[app].cmyk
        l.append("gsave")
        l.append("    0 0 0 1 setcmykcolor")
        l.append("    newpath")
        l.append("    %d %d moveto" % (position_lb.x, position_lb.y))
        l.append("    %d %d rlineto" % (csize.x, 0))
        l.append("    %d %d rlineto" % (0, csize.y))
        l.append("    %d %d rlineto" % (-csize.x, 0))
        l.append("    %d %d rlineto" % (0, -csize.y))
        l.append("    closepath")
        l.append("    gsave")
        l.append("        %f %f %f %f setcmykcolor" % (
                colour[0], colour[1], colour[2], colour[3]))
        l.append("        fill")
        l.append("    grestore")
        l.append("    stroke")
        l.append("grestore")
        text_position_lb = Position(
            x0.x + 4, x0.y + idx * distance_between_colour + 2)
        l.extend(_place_text(app, text_position_lb))
    return l


if __name__ == '__main__':
    pass

