"""
Luv class.

https://en.wikipedia.org/wiki/CIELUV
"""
from ..spaces import Space, Labish
from ..cat import WHITES
from ..gamut.bounds import GamutUnbound, FLG_OPT_PERCENT
from .lab import KAPPA, EPSILON, KE
from .. import util
from .. import algebra as alg
from ..types import Vector
from typing import Tuple


def xyz_to_luv(xyz: Vector, white: Tuple[float, float]) -> Vector:
    """XYZ to Luv."""

    u, v = util.xy_to_uv(util.xyz_to_xyY(xyz, white)[:2])
    w_xyz = util.xy_to_xyz(white)
    ur, vr = util.xy_to_uv(white)

    yr = xyz[1] / w_xyz[1]
    l = 116 * alg.nth_root(yr, 3) - 16 if yr > EPSILON else KAPPA * yr

    return [
        l,
        13 * l * (u - ur),
        13 * l * (v - vr),
    ]


def luv_to_xyz(luv: Vector, white: Tuple[float, float]) -> Vector:
    """Luv to XYZ."""

    l, u, v = luv
    w_xyz = util.xy_to_xyz(white)
    ur, vr = util.xy_to_uv(white)

    if l != 0:
        up = (u / (13 * l)) + ur
        vp = (v / (13 * l)) + vr
    else:
        up = vp = 0

    y = w_xyz[1] * (((l + 16) / 116) ** 3 if l > KE else l / KAPPA)

    if vp != 0:
        x = y * ((9 * up) / (4 * vp))
        z = y * ((12 - 3 * up - 20 * vp) / (4 * vp))
    else:
        x = z = 0

    return [x, y, z]


class Luv(Labish, Space):
    """Luv class."""

    BASE = "xyz-d65"
    NAME = "luv"
    SERIALIZE = ("--luv",)
    CHANNEL_NAMES = ("l", "u", "v")
    CHANNEL_ALIASES = {
        "lightness": "l"
    }
    WHITE = WHITES['2deg']['D65']

    BOUNDS = (
        GamutUnbound(0.0, 100.0, FLG_OPT_PERCENT),
        GamutUnbound(-175.0, 175.0),
        GamutUnbound(-175.0, 175.0)
    )

    @property
    def l(self) -> float:
        """L channel."""

        return self._coords[0]

    @l.setter
    def l(self, value: float) -> None:
        """Get true luminance."""

        self._coords[0] = value

    @property
    def u(self) -> float:
        """U channel."""

        return self._coords[1]

    @u.setter
    def u(self, value: float) -> None:
        """U axis."""

        self._coords[1] = value

    @property
    def v(self) -> float:
        """V channel."""

        return self._coords[2]

    @v.setter
    def v(self, value: float) -> None:
        """V axis."""

        self._coords[2] = value

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To XYZ D50 from Luv."""

        return luv_to_xyz(coords, cls.WHITE)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From XYZ D50 to Luv."""

        return xyz_to_luv(coords, cls.WHITE)
