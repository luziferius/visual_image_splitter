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
import pathlib

from PyQt5.QtCore import QObject, QAbstractTableModel, QModelIndex, QVariant, Qt

from .point import Point
from .rectangle import Rectangle
from .image import Image
from ._logger import get_logger

logger = get_logger("model")


class Selection(typing.NamedTuple):
    x1: str
    y1: str
    x2: str
    y2: str

    def to_rectangle(self, image_width: int, image_height: int):
        x1 = Selection._parse_first(self.x1, image_width)
        y1 = Selection._parse_first(self.y1, image_height)
        x2 = Selection._parse_second(self.x2, image_width, x1)
        y2 = Selection._parse_second(self.y2, image_height, y1)
        result = Rectangle(Point(x1, y1), Point(x2, y2))
        logger.info(f"Converting {self} into {result}")
        return result

    @staticmethod
    def _parse_first(value: str, image_dimension: int) -> int:
        result = Selection._parse_value(value, image_dimension)
        if result < 0:
            result = image_dimension + result  # Reminder: Because result is negative, this is the desired substraction
        return result

    @staticmethod
    def _parse_second(value: str, image_dimension: int, relative_anchor: int) -> int:
        result = Selection._parse_value(value, image_dimension)
        if result < 0 or value.startswith("+"):
            # Relative to the first anchor, positive or negative
            # Reminder: if result is negative, this is the intended substraction.
            result = relative_anchor + result
        return result

    @staticmethod
    def _parse_value(value: str, image_dimension: int) -> int:
        if value.endswith("%"):
            result = int(image_dimension * float(value[:-1]) / 100)
        else:
            result = int(value)
        return result


class Model(QAbstractTableModel):
    """
    Holds the Image data. This implements a Qt Model class.
    Column definitions:
     - 0: Image data
     - 1: Selection rectangles
     - 3: Output path
    """
    def __init__(self, args, parent: QObject=None):
        """

        :param args: Parsed command line arguments. Expects an argparse.Namespace object
        :param parent: Optional parent object
        """
        super(Model, self).__init__(parent)
        self.args = args
        logger.info(f"Creating Model instance. Arguments: {args}")
        # The predefined selections is a list of selections given on the command line. These selections are
        # automatically added to each Image file
        logger.info("Loading selections given on the command line")
        self.predefined_selections: typing.List[Selection] = self._create_selections_from_command_line()
        logger.debug(f"Loaded selections: {self.predefined_selections}")
        # Load all given images
        logger.info("Loading images given on the command line")
        self.images: typing.List[Image] = []
        self._open_command_line_given_images()

    def _create_selections_from_command_line(self):
        return [Selection(*selection) for selection in self.args.selections]

    def _open_command_line_given_images(self):
        """
        Open all images given as command line arguments.
        This automatically adds the selections predefined on the command line to each image file.
        """
        for image_path_str in self.args.images:
            image_path = pathlib.Path(image_path_str).expanduser()
            logger.debug(f"Create Image instance with Path: '{image_path}'")
            self.open_image(image_path)

    def open_image(self, path: pathlib.Path):
        """
        Open the image with the given path.
        This automatically adds the selections predefined on the command line to the given image file.
        """
        image = Image(path, self)
        logger.debug(f"Image instance created. Adding predefined selections as given on the command line: "
                     f"{self.predefined_selections}")
        for selection in self.predefined_selections:
            image.add_selection(selection.to_rectangle(image.width, image.height))
        self.images.append(image)
        image.clear_image_data()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.images)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 3

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        if index.row() < 0:
            # Invalid: negative row.
            return QVariant()
        try:
            image = self.images[index.row()]
        except IndexError:
            return QVariant()
        else:
            if role == Qt.DisplayRole:
                return self._get_column_display_data_for_row(index.column(), image)
            elif role == Qt.BackgroundRole:
                return self._get_background_data_for_row(index.column(), image)
            else:
                return QVariant()

    @staticmethod
    def _get_column_display_data_for_row(column: int, image: Image) -> QVariant:
        if column == 0:
            return QVariant(str(image.image_path))
        elif column == 1:
            return QVariant(str(image.selections))
        elif column == 2:
            return QVariant(str(image.output_path))
        else:
            # Invalid column
            return QVariant()

    @staticmethod
    def _get_background_data_for_row(column: int, image: Image) -> QVariant:
        if column == 0:
            return QVariant(image.low_resolution_image)
        else:
            return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return QVariant("Image")
            elif section == 1:
                return QVariant("Selections")
            elif section == 2:
                return QVariant("Output path")
        return QVariant()
