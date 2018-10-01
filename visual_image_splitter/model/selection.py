# Copyright (C) 2018 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import typing

from PyQt5.QtCore import QRect, QPoint, QSize, QRectF

from .point import Point

if typing.TYPE_CHECKING:
    from .image import Image


class Selection:

    def __init__(self, point1: Point, point2: Point, parent_image=None):
        self.top_left, self.bottom_right = Selection._normalize(point1, point2)
        self.parent: Image = parent_image

    @staticmethod
    def _normalize(point1: Point, point2: Point) -> typing.Tuple[Point, Point]:
        """
        Normalize coordinates given by two points. After normalization, the first point gives the top left corner,
        and the second point the bottom right corner.
        """
        top_left = Point(min(point1.x, point2.x), min(point1.y, point2.y))
        bottom_right = Point(max(point1.x, point2.x), max(point1.y, point2.y))
        return top_left, bottom_right

    @property
    def as_qrect(self) -> QRect:
        # Not using QRect(QPoint, QPoint), constructor, because: "There is a third constructor that creates a QRect
        # using the top-left and bottom-right coordinates, but we recommend that you avoid using it. The rationale is
        # that for historical reasons the values returned by the bottom() and right() functions deviate from the true
        # bottom-right corner of the rectangle." (http://doc.qt.io/qt-5/qrect.html#details)
        return QRect(
            QPoint(*self.top_left),
            QSize(self.bottom_right.x-self.top_left.x, self.bottom_right.y-self.top_left.y)
        )

    @property
    def as_qrectf(self) -> QRectF:
        return QRectF(QPoint(*self.top_left), QPoint(*self.bottom_right))

    @property
    def width(self) -> int:
        return self.bottom_right.x - self.top_left.x

    @property
    def height(self) -> int:
        return self.bottom_right.y - self.top_left.y

    def __repr__(self) -> str:
        return f"Selection({self.top_left}, {self.bottom_right})"

    def __str__(self) -> str:
        return repr(self)
