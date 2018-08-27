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
from PyQt5.QtGui import QImage, QImageReader, QImageWriter

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
        self.thumbnails: typing.Dict[Rectangle, Thumbnail] = {}
        self.output_path: Path = source_file.parent
        self.image_data: QImage = None

    def add_selection(self, selection: Rectangle):
        self.selections.append(selection)
        self.thumbnails[selection] = Thumbnail(self, selection)

    @property
    def has_image_data(self) -> bool:
        return self.image_data is not None

    def load_image_data(self) -> QImage:
        image_reader = QImageReader(str(self.image_path))
        if image_reader.canRead():
            self.image_data = image_reader.read()
            return self.image_data
        else:
            raise RuntimeError(f"Image {self.image_path} cannot be read.")

    def clear_image_data(self):
        """Images can be large at high resolutions, a 600DPI scanned image can be 100MiB in size. Keeping hundreds
        loaded at runtime is infeasible, so the image data has to be cleared if not used."""
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

    def write_output(self):
        if not self.has_image_data:
            self.load_image_data()
        progress_step_size = 100/(len(self.selections)*2)
        self.write_output_progress.emit(0)
        for index, selection in enumerate(self.selections, start=1):

            extract = self.image_data.copy(selection.as_qrect)
            self.write_output_progress.emit(int((2*index-1)*progress_step_size))
            writer = QImageWriter(self._get_output_file_name(index))
            if writer.canWrite():
                writer.write(extract)
            self.write_output_progress.emit(int((2*index)*progress_step_size))

    def _get_output_file_name(self, selection_index: int) -> str:
        path = self.output_path / f"{self.image_path.stem}_{selection_index:05}{self.image_path.suffix}"
        return str(path)

    def __repr__(self):
        return f"Image({self.image_path}, selection_count={len(self.selections)}, " \
               f"selections={self.selections}, output_path={self.output_path})"

    def __str__(self):
        return repr(self)


class Thumbnail:
    
    def __init__(self, source: Image, boundary: Rectangle=None):
        """

        :param source: The source image
        :param boundary: A Rectangle specifying the thumbnailed image part, clipped by the source dimensions.
        If not given, the whole source image is used.
        """
        self.source_image = source
        self.boundary = boundary
