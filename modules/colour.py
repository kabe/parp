#!/usr/bin/env python

# Colour Module


class ColourError(Exception):
    """Exception Class for Colours.
    """
    pass


class ColourConversionError(ColourError):
    """Exception in converting colour.
    """
    pass


class Colour(object):
    """Colour.
    """

    class RGB(object):
        """RGB class.
        """

        def _set_r(self, value):
            self._r = value

        def _get_r(self):
            return self._r

        def _set_g(self, value):
            self._g = value

        def _get_g(self):
            return self._g

        def _set_b(self, value):
            self._b = value

        def _get_b(self):
            return self._b

        r = property(_get_r, _set_r)
        g = property(_get_g, _set_g)
        b = property(_get_b, _set_b)

        def __init__(self, r, g, b):
            """

            Arguments:
            - `r`:
            - `g`:
            - `b`:
            """
            if not (0 <= r <= 1 and 0 <= g <= 1 and 0 <= b <= 1):
                raise ColourError("Colour info out of range")
            self._r = r
            self._g = g
            self._b = b

        def __getitem__(self, key):
            """Index support.

            @param key
            """
            if not isinstance(key, int):
                raise TypeError("Colour index must be integer")
            if key == 0:
                return self.r
            elif key == 1:
                return self.g
            elif key == 2:
                return self.b
            else:
                raise IndexError("Colour index out of range")

        def __len__(self, ):
            """Length.
            """
            return 3

        def __iter__(self, ):
            """Iteration Generator.
            """
            for x in (self.r, self.g, self.b):
                yield x

        def toYUV(self, ):
            """Convert RGB to YUV.

            Y =  0.299R + 0.587G + 0.114B
            U = -0.169R - 0.331G + 0.500B
            V =  0.500R - 0.419G - 0.081B
            """
            _y = 0.299 * self.r + 0.587 * self.g + 0.114 * self.b
            _u = -0.169 * self.r - 0.331 * self.g + 0.500 * self.b
            _v = 0.500 * self.r - 0.419 * self.g - 0.081 * self.b
            y = max(-0.5, min(_y, 0.5))
            u = max(-0.5, min(_u, 0.5))
            v = max(-0.5, min(_v, 0.5))
            yuv = Colour.YUV(y, u, v)
            return yuv

        def toCMYK(self, ):
            """Convert RGB to CMYK.
            """
            _r = 1.0 - self.r
            _g = 1.0 - self.g
            _b = 1.0 - self.b
            _k = min(_r, _g, _b)
            if _r == _g == _b == 1:
                _k = 0
            _c_ = (_r - _k) / (1.0 - _k)
            _m_ = (_g - _k) / (1.0 - _k)
            _y_ = (_b - _k) / (1.0 - _k)
            _k_ = _k
            c = max(0.0, min(_c_, 1.0))
            m = max(0.0, min(_m_, 1.0))
            y = max(0.0, min(_y_, 1.0))
            k = max(0.0, min(_k_, 1.0))
            cmyk = Colour.CMYK(c, m, y, k)
            return cmyk

    class CMYK(object):
        """CMYK class.
        """

        def _set_c(self, value):
            self._c = value

        def _get_c(self):
            return self._c

        def _set_m(self, value):
            self._m = value

        def _get_m(self):
            return self._m

        def _set_y(self, value):
            self._y = value

        def _get_y(self):
            return self._y

        def _set_k(self, value):
            self._k = value

        def _get_k(self):
            return self._k

        c = property(_get_c, _set_c)
        m = property(_get_m, _set_m)
        y = property(_get_y, _set_y)
        k = property(_get_k, _set_k)

        def __init__(self, c, m, y, k):
            """

            @param c
            @param m
            @param y
            @param k
            """
            if not (0 <= c <= 1 and 0 <= m <= 1 and
                    0 <= y <= 1 and 0 <= k <= 1):
                raise ColourError("Colour info out of range")
            self._c = c
            self._m = m
            self._y = y
            self._k = k

        def __getitem__(self, key):
            """Index support.

            @param key
            """
            if not isinstance(key, int):
                raise TypeError("Colour index must be integer")
            if key == 0:
                return self.c
            elif key == 1:
                return self.m
            elif key == 2:
                return self.y
            elif key == 3:
                return self.k
            else:
                raise IndexError("Colour index out of range")

        def __len__(self, ):
            """Length.
            """
            return 4

        def __iter__(self, ):
            """Iteration Generator.
            """
            for x in (self.c, self.m, self.y, self.k):
                yield x

        def toRGB(self, ):
            """Convert to RGB.
            """
            _r = 1.0 - min(1, self.c * (1.0 - self.k) + self.k)
            _g = 1.0 - min(1, self.m * (1.0 - self.k) + self.k)
            _b = 1.0 - min(1, self.y * (1.0 - self.k) + self.k)
            r = max(0.0, min(_r, 1.0))
            g = max(0.0, min(_g, 1.0))
            b = max(0.0, min(_b, 1.0))
            rgb = Colour.RGB(r, g, b)
            return rgb

        def toYUV(self, ):
            """Convert to YUV.
            """
            return self.toRGB().toYUV()

    class YUV(object):
        """YUV class.
        """

        def _set_y(self, value):
            self._y = value

        def _get_y(self):
            return self._y

        def _set_u(self, value):
            self._u = value

        def _get_u(self):
            return self._u

        def _set_v(self, value):
            self._v = value

        def _get_v(self):
            return self._v

        y = property(_get_y, _set_y)
        u = property(_get_u, _set_u)
        v = property(_get_v, _set_v)

        def __init__(self, y, u, v):
            """

            @param y
            @param u
            @param v
            """
            if not (0 <= y <= 1 and -0.5 <= u <= 0.5 and -0.5 <= v <= 0.5):
                raise ColourError("Colour info out of range")
            self._y = y
            self._u = u
            self._v = v

        def __getitem__(self, key):
            """Index support.

            @param key
            """
            if not isinstance(key, int):
                raise TypeError("Colour index must be integer")
            if key == 0:
                return self.r
            elif key == 1:
                return self.g
            elif key == 2:
                return self.b
            else:
                raise IndexError("Colour index out of range")

        def __len__(self, ):
            """Length.
            """
            return 3

        def __iter__(self, ):
            """Iteration Generator.
            """
            for x in (self.y, self.u, self.v):
                yield x

        def toRGB(self, ):
            """Convert YUV to RGB.

            R = 1.000Y          + 1.402V
            G = 1.000Y - 0.344U - 0.714V
            B = 1.000Y + 1.772U
            """
            _r = 1.000 * self.y + 1.402 * self.v
            _g = 1.000 * self.y - 0.344 * self.u - 0.714 * self.v
            _b = 1.000 * self.y + 1.772 * self.u
            r = max(0.0, min(_r, 1.0))
            g = max(0.0, min(_g, 1.0))
            b = max(0.0, min(_b, 1.0))
            rgb = Colour.RGB(r, g, b)
            return rgb

        def toCMYK(self, ):
            """Convert to CMYK.
            """
            return self.toRGB().toCMYK()

    def _set_rgb(self, value):
        self._rgb = value

    def _get_rgb(self):
        if not self._rgb:
            if self._cmyk:
                self._rgb = self._cmyk.toRGB()
            elif self._yuv:
                self._rgb = self._yuv.toRGB()
            else:
                ColourConversionError(
                    "Object does not have colour information")
        return self._rgb

    def _set_cmyk(self, value):
        self._cmyk = value

    def _get_cmyk(self):
        if not self._cmyk:
            if self._rgb:
                self._cmyk = self._rgb.toCMYK()
            elif self._yuv:
                self._cmyk = self._yuv.toCMYK()
            else:
                ColourConversionError(
                    "Object does not have colour information")
        return self._cmyk

    def _set_yuv(self, value):
        self._yuv = value

    def _get_yuv(self):
        if not self._yuv:
            if self._rgb:
                self._yuv = self._rgb.toYUV()
            elif self._cmyk:
                self._yuv = self._cmyk.toYUV()
            else:
                ColourConversionError(
                    "Object does not have colour information")
        return self._yuv

    rgb = property(_get_rgb, _set_rgb)
    cmyk = property(_get_cmyk, _set_cmyk)
    yuv = property(_get_yuv, _set_yuv)

    def __init__(self, ):
        """
        """
        self._rgb = None
        self._cmyk = None
        self._yuv = None

    def __repr__(self, ):
        """Representation form.
        """
        s = "<colour.Colour %s>"
        rgbform = "rgb=#%02X%02X%02X" % (min(255, int(self.rgb.r * 255.0)),
                                         min(255, int(self.rgb.g * 255.0)),
                                         min(255, int(self.rgb.b * 255.0)))
        return s % (rgbform)


def rgb(r, g, b):
    """Dummy constructor of Colour initialized with an RGB colour.
    """
    obj = Colour()
    obj.rgb = Colour.RGB(r, g, b)
    return obj


def cmyk(c, m, y, k):
    """Dummy constructor of Colour initialized with an CMYK colour.
    """
    obj = Colour()
    obj.cmyk = Colour.CMYK(c, m, y, k)
    return obj


def yuv(y, u, v):
    """Dummy constructor of Colour initialized with an YUV colour.
    """
    obj = Colour()
    obj.yuv = Colour.YUV(y, u, v)
    return obj


# Colour gradation

def rgb_gradation(n, c0, c1):
    """Create a gradation colour of RGB.

    @param n # of colours
    @param c0 Colour from
    @param c1 Colour to
    """
    ca0 = [c0.rgb.r, c0.rgb.g, c0.rgb.b]
    ca1 = [c1.rgb.r, c1.rgb.g, c1.rgb.b]
    _cg = mk_colour_gradation(n, ca0, ca1)
    cg = [rgb(c[0], c[1], c[2]) for c in _cg]
    return cg


def cmyk_gradation(n, c0, c1):
    """Create a gradation colour of CMYK.

    @param n # of colours
    @param c0 Colour from
    @param c1 Colour to
    """
    ca0 = [c0.cmyk.c, c0.cmyk.m, c0.cmyk.y, c0.cmyk.k]
    ca1 = [c1.cmyk.c, c1.cmyk.m, c1.cmyk.y, c1.cmyk.k]
    _cg = mk_colour_gradation(n, ca0, ca1)
    cg = [cmyk(c[0], c[1], c[2], c[3]) for c in _cg]
    return cg


def yuv_gradation(n, c0, c1):
    """Create a gradation colour of YUV.

    @param n # of colours
    @param c0 Colour from
    @param c1 Colour to
    """
    ca0 = [c0.yuv.y, c0.yuv.u, c0.yuv.v]
    ca1 = [c1.yuv.y, c1.yuv.u, c1.yuv.v]
    _cg = mk_colour_gradation(n, ca0, ca1)
    cg = [yuv(c[0], c[1], c[2]) for c in _cg]
    return cg


def mk_colour_gradation(n, c0, c1):
    """Create a gradation colour array.

    @param n # of colours
    @param c0 Colour array from
    @param c1 Colour array to
    """
    colours = []
    for idx in xrange(n):
        c = [0] * len(c0)
        for cel in range(len(c0)):
            c[cel] = (
                (1.0 * idx * c0[cel] + (n - 1.0 - idx) * c1[cel]) /
                (n - 1.0))
        colours.append(c)
    return colours
