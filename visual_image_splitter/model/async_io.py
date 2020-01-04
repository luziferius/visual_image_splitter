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

from PyQt5.QtCore import QObject, pyqtSlot, QModelIndex

from visual_image_splitter.logger import get_logger
logger = get_logger(__name__)
del get_logger


class ModelWorker(QObject):
    """
    This class is a simple wrapper around time consuming model functions. It is derived from QObject, so that it
    can be moved to another thread using the QObject.moveToThread(thread) function. It resides inside a worker thread
    to perform those long running operations in the background.
    """

    def __init__(self, model, parent: QObject = None):
        super(ModelWorker, self).__init__(parent)
        self.model = model
        logger.info("Created ModelWorker instance for asynchronous file operations.")

    @pyqtSlot()
    def open_command_line_given_images(self):
        logger.info("Opening images specified on the command line")
        self.model._open_command_line_given_images()

    @pyqtSlot()
    def save_and_close_all_images(self):
        logger.info("Saving and closing all opened images.")
        self.model._save_and_close_all_images()

    @pyqtSlot(list)
    def open_images(self, path_list: typing.Iterable[pathlib.Path]):
        logger.info("Opening a list of files")
        self.model._open_images(path_list)

    @pyqtSlot(QModelIndex, bool)
    def close_image(self, model_index: QModelIndex, save_selections: bool):
        logger.info(f"Closing a file. Index={model_index}, Save selections={save_selections}")
        self.model._close_image(model_index, save_selections)
