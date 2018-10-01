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

import pytest
from hamcrest import *

from visual_image_splitter.model.point import Point
from visual_image_splitter.model.rectangle import Rectangle
from visual_image_splitter.model.model import SelectionPreset


def rectangle(x1: int, y1: int, x2: int, y2: int) -> Rectangle:
    """Save some typing."""
    return Rectangle(Point(x1, y1), Point(x2, y2))


def generate_selection_preset_to_rectangle_conversion_test_cases():
    """Yields tuples containing a SelectionPreset, image_width, image_height, expected Rectangle """

    # Positive absolute coordinates
    yield SelectionPreset("100", "50", "300", "400"), 1000, 1000, rectangle(100, 50, 300, 400)
    yield SelectionPreset("100", "50", "20%", "400"), 1000, 1000, rectangle(100, 50, 200, 400)
    yield SelectionPreset("100%", "50%", "10%", "5%"), 1000, 1000, rectangle(100, 50, 1000, 500)

    # Negative absolute coordinates
    yield SelectionPreset("-100", "-50", "300", "400"), 1000, 1000, rectangle(300, 400, 900, 950)  # Both values negative
    yield SelectionPreset("-100", "50", "300", "400"), 1000, 1000, rectangle(300, 50, 900, 400)  # One value negative
    yield SelectionPreset("-10%", "-50%", "300", "0"), 1000, 1000, rectangle(300, 0, 900, 500)  # Both percentages negative

    # Corner case: Negative zero coordinates. These are relative to the bottom/right border
    yield SelectionPreset("-0%", "-100", "300", "0"), 1000, 1000, rectangle(300, 0, 1000, 900)
    yield SelectionPreset("-0", "-100", "300", "0"), 1000, 1000, rectangle(300, 0, 1000, 900)
    yield SelectionPreset("-0", "-0", "50", "50"), 1000, 1000, rectangle(50, 50, 1000, 1000)
    yield SelectionPreset("0", "-0", "50", "50"), 1000, 1000, rectangle(0, 50, 50, 1000)

    # Relative mode
    yield SelectionPreset("100", "50", "+300", "+100"), 1000, 1000, rectangle(100, 50, 400, 150)
    yield SelectionPreset("500", "400", "-300", "+200"), 1000, 1000, rectangle(200, 400, 500, 600)
    yield SelectionPreset("500", "350", "-10%", "+200"), 1000, 1000, rectangle(400, 350, 500, 550)
    yield SelectionPreset("-60%", "-400", "-300", "+200"), 1000, 1000, rectangle(100, 600, 400, 800)


@pytest.mark.parametrize("selection, image_width, image_height, expected_rectangle",
                         generate_selection_preset_to_rectangle_conversion_test_cases())
def test_selection_preset_to_rectangle_conversion(selection, image_width, image_height, expected_rectangle):
    result = selection.to_rectangle(image_width, image_height)
    assert_that(result.top_left, is_(equal_to(expected_rectangle.top_left)))
    assert_that(result.bottom_right, is_(equal_to(expected_rectangle.bottom_right)))
