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

from pathlib import Path
import typing
import enum

from PyQt5.QtCore import pyqtSignal, QObject, QThread, QVariant, Qt
from PyQt5.QtGui import QImage, QImageReader, QImageWriter, QPixmap
from PyQt5.QtWidgets import QApplication

from .selection import Selection
from ._logger import get_logger

if typing.TYPE_CHECKING:
    from .model import Model

logger = get_logger("Image")


@enum.unique
class Columns(enum.IntEnum):
    IMAGE = 0
    IMAGE_PATH = 1
    OUTPUT_PATH = 2


class Image(QObject):
    """This class models an opened image file."""
    write_output_progress = pyqtSignal(int)

    QT_COLUMN_COUNT = 3  # Number of columns. Used in the Qt Model API.

    def __init__(self, source_file: Path, parent: QObject=None):
        super(Image, self).__init__(parent)
        self.image_path: Path = source_file.expanduser()
        self.selections: typing.List[Selection] = []
        self.thumbnails: typing.Dict[Selection, QPixmap] = {}
        self.low_resolution_image: QPixmap = None
        self.output_path: Path = source_file.parent
        self.image_data: QImage = None
        self._width: int = None
        self._height: int = None
        self.load_meta_data()
        logger.info(f"Created Image instance with source file: {source_file}")

    def load_meta_data(self):
        if not self.has_image_data:
            self.load_image_data()
        self._width = self.image_data.width()
        self._height = self.image_data.height()
        logger.debug(f"Scaling low resolution image to resolution: {self._scaled_to_resolution(800)}")
        self.low_resolution_image = QPixmap.fromImage(
            self.image_data.scaled(*self._scaled_to_resolution(800), transformMode=Qt.SmoothTransformation)
        )

    def add_selection(self, selection: Selection):
        """
        Add a selection for this Image.
        When saving, this selection will be extracted and saved as an image file to disk.
        :param selection: the to be added Selection
        """
        logger.info(f"Adding a new selection: {selection}")
        self.selections.append(selection)
        self.thumbnails[selection] = self.low_resolution_image.copy(selection.as_qrect)

    def row_count(self) -> int:
        """Returns the number of selections. This is the number of child rows in the Qt TreeModel."""
        return len(self.selections)

    @staticmethod
    def column_count() -> int:
        """Number of Qt TreeModel columns. This contains the image data, image path and the output path."""
        return 3

    def data(self, column: int, role: int=Qt.DisplayRole) -> QVariant:
        """Qt Model function. Returns the own data using the Qt model API"""
        if column not in range(0, Selection.QT_COLUMN_COUNT):
            # Short-cut invalid columns now
            return QVariant()

        if role == Qt.DisplayRole:
            return self._get_column_display_data_for_row(column)
        elif role == Qt.BackgroundRole:
            return self._get_background_data_for_row(column)
        elif role == Qt.UserRole:
            return self._get_user_data_for_row(column)
        else:
            return QVariant()

    def _get_column_display_data_for_row(self, column: int) -> QVariant:
        if column == Columns.IMAGE:
            return QVariant(str(self.low_resolution_image))
        elif column == Columns.IMAGE_PATH:
            return QVariant(str(self.image_path))
        elif column == Columns.OUTPUT_PATH:
            return QVariant(str(self.output_path))

    def _get_background_data_for_row(self, column: int) -> QVariant:
        if column == Columns.IMAGE:
            return QVariant(self.low_resolution_image)
        else:
            return QVariant()

    def _get_user_data_for_row(self, column: int):
        if column == Columns.IMAGE:
            return QVariant(self)
        elif column == Columns.IMAGE_PATH:
            return QVariant(self.image_path)
        elif column == Columns.OUTPUT_PATH:
            return QVariant(self.output_path)

    def row(self) -> int:
        """Qt Model function. Returns the own row, that is the own position inside the parent image list."""
        if self.parent() is None:
            row = 0
        else:
            # Look up the own position (row) in the parent model class.
            model: Model = self.parent()
            row = model.images.index(self)
        return row

    def child(self, row: int) -> Selection:
        """Qt Model function. Returns the Selection at the given child row. or None, if it does not exist."""
        return self.selections[row] if 0 <= row < len(self.selections) else None

    @property
    def has_image_data(self) -> bool:
        return self.image_data is not None

    def load_image_data(self) -> QImage:
        """
        Loads the image data from disk. This has to be called when the file content needs to be accessed.
        :return:
        """
        logger.debug(f"Requested loading image data from the hard disk. File: {self.image_path}")
        image_reader = QImageReader(str(self.image_path))
        if image_reader.canRead():
            logger.debug("Image data can be read, performing file reading…")
            self.image_data = image_reader.read()
            logger.info(
                f"File reading done. Loaded image dimensions: "
                f"x={self.image_data.width()}, y={self.image_data.height()}, format={self.image_data.format()}"
            )
            return self.image_data
        else:
            raise RuntimeError(f"Image {self.image_path} cannot be read.")

    def clear_image_data(self):
        """Images can be large at high resolutions, a 600DPI scanned image can be over 100MiB in size. Keeping hundreds
        loaded at runtime is infeasible, so the image data has to be cleared if not used."""
        if self.image_data is not None:
            logger.debug(f"Deleting loaded image file data for Image {self.image_path}.")
            self.image_data = None

    def remove_selection(self, selection: typing.Union[int, Selection]):
        if isinstance(selection, Selection):
            try:
                self.selections.remove(selection)
            except ValueError:
                raise  # TODO: Is this an error?
            else:
                del self.thumbnails[selection]
        else:
            del self.thumbnails[self.selections[selection]]
            del self.selections[selection]

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def write_output(self):
        """
        Writes all selections as output files to disk.
        :return:
        """
        logger.info(f"Starting to extract selections and writing output files for image {self.image_path}")
        if not self.selections:
            logger.debug("Image has no selections, do nothing.")
            return
        if not self.has_image_data:
            self.load_image_data()
        progress_step_size = 100/(len(self.selections)*2)
        self.write_output_progress.emit(0)
        worker_thread: QThread = QApplication.instance().model.worker_thread
        for index, selection in enumerate(self.selections, start=1):
            if worker_thread.isInterruptionRequested():
                logger.warning("Requested worker thread interruption. Aborting writing selections to files.")
                break
            self._write_selection_to_output_file(index, selection, progress_step_size)

    def _write_selection_to_output_file(self, index: int, selection: Selection, progress_step_size: float):
        """
        Creates a new image file and writes the content of the given selection to disk.
        :param index: The index of this selection. This is used to build increasing file numbers for the output file.
        :param selection: The Selection in progress
        :param progress_step_size: Float giving the current progress step size per file in percent. Used for progress
        notifications and logging purposes.
        :return:
        """
        extract = self.image_data.copy(selection.as_qrect)
        self.write_output_progress.emit(int((2 * index - 1) * progress_step_size))
        logger.debug(f"Extracted selection. Progress: {(2*index-1)*progress_step_size:2.2f}%")
        writer = QImageWriter(self._get_output_file_name(index))
        if writer.canWrite():
            writer.write(extract)
            logger.debug(f"Written extracted selection to disk. Progress: {(2*index)*progress_step_size:2.2f}%")
        else:
            logger.warning(f"Image data can not be written! Offending File: {writer.fileName()}")
        self.write_output_progress.emit(int((2 * index) * progress_step_size))

    def _get_output_file_name(self, selection_index: int) -> str:
        path = self.output_path / f"{self.image_path.stem}_{selection_index:05}{self.image_path.suffix}"
        return str(path)

    def _scaled_to_resolution(self, maximum: int=1000) -> typing.Tuple[float, float]:
        scaling_factor = maximum / max(self.width, self.height)
        if scaling_factor > 1:
            return self.width, self.height
        return self.width * scaling_factor, self.height * scaling_factor

    def __repr__(self):
        return f"Image({self.image_path}, selection_count={len(self.selections)}, " \
               f"selections={self.selections}, output_path={self.output_path})"

    def __str__(self):
        return repr(self)
