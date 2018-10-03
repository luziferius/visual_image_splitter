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

from PyQt5.QtCore import QRect, QPoint, QSize, QRectF, QVariant, Qt

from .point import Point

if typing.TYPE_CHECKING:
    from .image import Image


class Selection:

    QT_COLUMN_COUNT = 2  # Number of columns. Used in the Qt Model API.

    def __init__(self, point1: Point, point2: Point, parent_image=None):
        self.top_left, self.bottom_right = Selection._normalize(point1, point2)
        self._parent: Image = parent_image

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

    @staticmethod
    def column_count() -> int:
        """Qt Model function."""
        return 2

    @staticmethod
    def row_count() -> int:
        """Qt Model function."""
        return 0

    def row(self) -> int:
        """
        Qt Model function. This function returns this selections own row number. It is used to create QModelIndex
        instances.
        """
        if self.parent is None:
            return 0
        else:
            return self.parent().selections.index(self)

    def data(self, column: int, role: int=Qt.DisplayRole) -> QVariant:
        """Qt Model function. Returns the own data using the Qt Model API"""
        if column not in range(0, Selection.QT_COLUMN_COUNT):
            # Short-cut invalid columns now
            return QVariant()

        if role == Qt.DisplayRole:
            return self._get_column_display_data_for_row(column)
        elif role == Qt.UserRole:
            return self._get_user_data_for_row(column)
        else:
            return QVariant()

    def _get_column_display_data_for_row(self, column: int) -> QVariant:
        """Returns column data for Qt.DisplayRole. REQUIRES a valid column index."""
        if column == 0:
            return QVariant(str(self.top_left))
        elif column == 1:
            return QVariant(str(self.bottom_right))

    def _get_user_data_for_row(self, column: int):
        """Returns column data for Qt.UserRole. REQUIRES a valid column index."""
        if column == 0:
            return QVariant(self.top_left)
        elif column == 1:
            return QVariant(self.bottom_right)

    def child(self, row: int):
        """
        Part of the tree model. Keeps the API stable for mixed types. Selection never has children.
        row_count() always returns zero, so this function should never be called by Qt model views.
        """
        del row   # No unused parameter…
        return None

    def parent(self):
        return self._parent

    @property
    def as_qrectf(self) -> QRectF:
        """Converts the selection to a QRectF. This is used by the SelectionScene QGraphicsScene to draw Selections."""
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
