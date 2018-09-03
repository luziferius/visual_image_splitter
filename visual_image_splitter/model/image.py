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

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QImage, QImageReader, QImageWriter, QPixmap

from .rectangle import Rectangle
from ._logger import get_logger

logger = get_logger("Image")


class Image(QObject):
    """"""
    write_output_progress = pyqtSignal(int)

    def __init__(self, source_file: Path, parent: QObject=None):
        super(Image, self).__init__(parent)
        self.image_path: Path = source_file.expanduser()
        self.selections: typing.List[Rectangle] = []
        self.thumbnails: typing.Dict[Rectangle, QPixmap] = {}
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
        self.low_resolution_image = QPixmap.fromImage(self.image_data.scaled(*self._scaled_to_resolution(800)))

    def add_selection(self, selection: Rectangle):
        """
        Add a selection for this Image.
        When saving, this selection will be extracted and saved as an image file to disk.
        :param selection: A Rectangle defining the selection
        """
        logger.info(f"Adding a new selection: {selection}")
        self.selections.append(selection)
        self.thumbnails[selection] = self.low_resolution_image.copy(selection.as_qrect)

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

    def remove_selection(self, selection: typing.Union[int, Rectangle]):
        if isinstance(selection, Rectangle):
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
        Writes
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
        for index, selection in enumerate(self.selections, start=1):
            self._write_selection_to_output_file(index, selection, progress_step_size)

    def _write_selection_to_output_file(self, index: int, selection: Rectangle, progress_step_size: float):
        """
        Creates a new image file and writes the content of the given selection to disk.
        :param index: The index of this selection. This is used to build increasing file numbers for the output file.
        :param selection: The selection Rectangle in progress
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
