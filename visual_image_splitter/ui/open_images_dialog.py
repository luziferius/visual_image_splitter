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

from PyQt5.QtGui import QImageReader, QImageWriter
from PyQt5.QtWidgets import QFileDialog, QWidget

from visual_image_splitter.logger import get_logger
logger = get_logger(__name__)
del get_logger


class OpenImagesDialog(QFileDialog):
    """
    This Dialog is used to open and load new image files.
    """

    def __init__(self, parent: QWidget = None):
        super(OpenImagesDialog, self).__init__(
            parent,
            "Open Image files",
            filter=self._get_supported_image_format_filter()
        )
        self.setFileMode(QFileDialog.ExistingFiles)  # Allow selecting multiple existing files.

    @staticmethod
    def _get_supported_image_format_filter() -> str:
        """
        Returns a filters string containing file type filters for image files.
        It is used to populate the file dialog type filter combo box.
        The filters contain an "All supported image formats" filter, a filter for each individual supported image format
        and a "All files" filter that disables filtering. The last is only useful for advanced purposes, for example
        when file type endings are missing in file names.
        :return:
        """
        supported_formats = OpenImagesDialog._supported_file_formats()
        logger.debug(f"Readable and writable image formats: {supported_formats}")
        formats_wildcards = [f"*.{file_format}" for file_format in supported_formats]
        all_images_filter = f"All supported image formats({' '.join(formats_wildcards)})"
        specific_filters_list = [
            f"{file_format.upper()}-File({wildcard})"
            for file_format, wildcard
            in zip(supported_formats, formats_wildcards)
        ]
        filters = f"{all_images_filter};;{';;'.join(specific_filters_list)};;All files(*)"
        logger.debug(f"Filter list in use: '{filters}'")
        return filters

    @staticmethod
    def _supported_file_formats() -> typing.List[str]:
        """
        Returns all supported file types. This is the intersection of readable and writable file formats.
        """
        supported_input_formats = set(f.data().decode("utf-8") for f in QImageReader.supportedImageFormats())
        supported_output_formats = set(f.data().decode("utf-8") for f in QImageWriter.supportedImageFormats())
        supported_formats = sorted(list(supported_input_formats.intersection(supported_output_formats)))
        return supported_formats

    def selected_paths(self) -> typing.List[Path]:
        """Returns a list with all selected files."""
        supported_formats = set(self._supported_file_formats())
        result = [Path(file_path_string) for file_path_string in self.selectedFiles()]
        for path in result:
            if not path.suffix or path.suffix.lower()[1:] not in supported_formats:
                logger.warning(f"Selected a file with an unknown file ending. Opening it will be tried, "
                               f"but will fail if it does not contain a known image format. File: {path}")
        return result
