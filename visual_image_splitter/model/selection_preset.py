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

from visual_image_splitter.model.image import Image
from visual_image_splitter.model.point import Point
from visual_image_splitter.model.selection import Selection

from visual_image_splitter.logger import get_logger
logger = get_logger(__name__)
del get_logger


class SelectionPreset(typing.NamedTuple):
    """
    The SelectionPreset is a selection preset that causes a Selection to be added to each opened image.
    The class supports absolute and relative selection specification, including negative coordinates and percentages,
    which will be converted to actual widths and heights for each image it is applied to.
    """

    x1: str
    y1: str
    x2: str
    y2: str

    def to_rectangle(self, image: Image):
        x1 = SelectionPreset._parse_first(self.x1, image.width)
        y1 = SelectionPreset._parse_first(self.y1, image.height)
        x2 = SelectionPreset._parse_second(self.x2, image.width, x1)
        y2 = SelectionPreset._parse_second(self.y2, image.height, y1)
        result = Selection(Point(x1, y1), Point(x2, y2), image)
        logger.info(f"Converting {self} into {result}")
        return result

    @staticmethod
    def _parse_first(value: str, image_dimension: int) -> int:
        result = SelectionPreset._parse_value(value, image_dimension)
        if result < 0 or (result == 0 and value.startswith("-")):
            # Second case is triggered, if specifying "-0" on the command line. This will use the right or bottom border
            # Reminder: Because result is non-positive, this is the desired subtraction:
            result = image_dimension + result
        return result

    @staticmethod
    def _parse_second(value: str, image_dimension: int, relative_anchor: int) -> int:
        result = SelectionPreset._parse_value(value, image_dimension)
        if result < 0 or value.startswith("+") or (result == 0 and value.startswith("-")):
            # Relative to the first anchor, positive or negative
            # Reminder: Because result is non-positive, this is the desired subtraction:
            result = relative_anchor + result
        return result

    @staticmethod
    def _parse_value(value: str, image_dimension: int) -> int:
        if value.endswith("%"):
            result = round(image_dimension * float(value[:-1]) / 100)
        else:
            result = int(value)
        return result
