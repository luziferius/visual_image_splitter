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

import pytest
from hamcrest import *

from visual_image_splitter.model.point import Point
from visual_image_splitter.model.rectangle import Rectangle


class RectangleData(typing.NamedTuple):
    point1: Point
    point2: Point


def generate_normalisation_test_cases():
    """Yields test cases for rectangle normalisation as tuples.
    First element is the input data, second element is the expected, normalized result."""

    # Regular rectangles
    yield RectangleData(Point(5, 10), Point(20, 40)), RectangleData(Point(5, 10), Point(20, 40))
    yield RectangleData(Point(20, 40), Point(5, 10)), RectangleData(Point(5, 10), Point(20, 40))
    yield RectangleData(Point(0, 50), Point(30, 10)), RectangleData(Point(0, 10), Point(30, 50))
    yield RectangleData(Point(30, 10), Point(0, 50)), RectangleData(Point(0, 10), Point(30, 50))
    # Both points on a line
    yield RectangleData(Point(0, 20), Point(0, 10)), RectangleData(Point(0, 10), Point(0, 20))
    yield RectangleData(Point(0, 10), Point(0, 10)), RectangleData(Point(0, 10), Point(0, 10))

    # Negative coordinates
    yield RectangleData(Point(5, 10), Point(20, -40)), RectangleData(Point(5, -40), Point(20, 10))
    yield RectangleData(Point(-20, 40), Point(5, 10)), RectangleData(Point(-20, 10), Point(5, 40))
    yield RectangleData(Point(0, 50), Point(-30, -10)), RectangleData(Point(-30, -10), Point(0, 50))
    yield RectangleData(Point(-30, -10), Point(0, -50)), RectangleData(Point(-30, -50), Point(0, -10))


@pytest.mark.parametrize("input_points, expected", generate_normalisation_test_cases())
def test__normalize(input_points: RectangleData, expected: RectangleData):
    """Test rectangle normalisation."""
    rectangle = Rectangle(*input_points)
    assert_that(rectangle.top_left, is_(equal_to(expected.point1)))
    assert_that(rectangle.bottom_right, is_(equal_to(expected.point2)))


@pytest.mark.parametrize("input_points, expected", generate_normalisation_test_cases())
def test_q_rect_conversion(input_points: RectangleData, expected: RectangleData):
    """Test conversion into QRect rectangles used for Qt5 interoperation."""
    q_rectangle = Rectangle(*input_points).as_qrect

    assert_that(q_rectangle.topLeft().x(), is_(equal_to(expected.point1.x)))
    assert_that(q_rectangle.topLeft().y(), is_(equal_to(expected.point1.y)))
    assert_that(q_rectangle.bottomRight().x(), is_(equal_to(expected.point2.x-1)))  # QRect is always one off
    assert_that(q_rectangle.bottomRight().y(), is_(equal_to(expected.point2.y-1)))  # QRect is always one off


@pytest.mark.parametrize("input_points, expected", generate_normalisation_test_cases())
def test_q_rectf_conversion(input_points: RectangleData, expected: RectangleData):
    """Test conversion into QRectF rectangles used for Qt5 interoperation."""
    q_rectangle = Rectangle(*input_points).as_qrectf

    assert_that(q_rectangle.topLeft().x(), is_(equal_to(expected.point1.x)))
    assert_that(q_rectangle.topLeft().y(), is_(equal_to(expected.point1.y)))
    assert_that(q_rectangle.bottomRight().x(), is_(equal_to(expected.point2.x)))
    assert_that(q_rectangle.bottomRight().y(), is_(equal_to(expected.point2.y)))
