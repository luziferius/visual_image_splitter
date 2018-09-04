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
            image_path = pathlib.Path(image_path_str).expanduser().resolve()
            logger.debug(f"Create Image instance with Path: '{image_path}'")
            self.open_image(image_path)

    def open_images(self, path_list: typing.Iterable[pathlib.Path]):
        for image_path in path_list:
            self.open_image(image_path)

    def add_selection(self, index: QModelIndex, selection: Rectangle):
        """
        Add a selection to the referenced image.
        """
        image = self.images[index.row()]
        self.beginInsertRows(index, len(image.selections), len(image.selections))
        self.dataChanged.emit(self.index(index.row(), 1), self.index(index.row(), 1))  # TODO: Temporary.
        # TODO: remove emitting dataChanged when the model is a proper tree and the view properly renders it.
        image.selections.append(selection)
        self.endInsertRows()

    def open_image(self, path: pathlib.Path):
        """
        Open the image with the given path.
        This automatically adds the selections predefined on the command line to the given image file.
        """
        self.beginInsertRows(QModelIndex(), len(self.images), len(self.images))
        image = Image(path, self)
        logger.debug(f"Image instance created. Adding predefined selections as given on the command line: "
                     f"{self.predefined_selections}")
        for selection in self.predefined_selections:
            image.add_selection(selection.to_rectangle(image.width, image.height))
        self.images.append(image)
        image.clear_image_data()
        self.endInsertRows()

    def save_and_close_all_images(self):
        """Save and close all images. This writes all selections to separate files, then closes all files."""
        logger.info("Writing all selections and closing all opened image files.")
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount()-1)
        for image in self.images:
            logger.debug(f"Writing output files for {image}")
            image.write_output()
        self.images.clear()
        self.endRemoveRows()

    def close_image(self, model_index: QModelIndex, save_selections: bool=True):
        """Save and close a single image file."""
        if model_index.isValid() and not model_index.parent().isValid() and model_index.row() < self.rowCount():
            row = model_index.row()
            logger.info(f"Closing file at row {row}. File: {self.images[row]}, write selections: {save_selections}")
            self.beginRemoveRows(QModelIndex(), row, row)
            if save_selections:
                self.images[row].write_output()
            del self.images[row]
            self.endRemoveRows()
        else:
            logger.warning(f"Got invalid model index: {model_index}")

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid() or (parent.isValid() and 1 == parent.column()):
            return super(Model, self).index(row, column, parent)

        if parent.row() > len(self.images):
            return QModelIndex()

        child_item = self.images[parent.row()]
        if len(child_item.selections) > row >= 0 == column:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and not parent.parent().isValid():
            if parent.column() == 1:
                try:
                    return len(self.images[parent.row()].selections)
                except IndexError:
                    return 0
        return len(self.images)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.column() == 1:
            return 1
        else:
            return 3

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        if not index.isValid():
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
            elif role == Qt.UserRole:
                return self._get_user_data_for_row(index.column(), image)
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

    @staticmethod
    def _get_user_data_for_row(column: int, image: Image):
        if column == 0:
            return QVariant(image)
        elif column == 1:
            return QVariant(image.selections)
        elif column == 2:
            return QVariant(image.output_path)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return QVariant("Image")
            elif section == 1:
                return QVariant("Selections")
            elif section == 2:
                return QVariant("Output path")
        return QVariant()
