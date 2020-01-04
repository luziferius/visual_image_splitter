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

from PyQt5.QtCore import QObject, QAbstractItemModel, QModelIndex, QVariant, Qt, QThread, pyqtSignal, QTimer

from visual_image_splitter.argument_parser import Namespace
from visual_image_splitter.model.selection_preset import SelectionPreset
from .selection import Selection
from .image import Image, Columns as ImageColumns
from .async_io import ModelWorker

from visual_image_splitter.logger import get_logger
logger = get_logger(__name__)
del get_logger


class Model(QAbstractItemModel):
    """
    Holds the Image data. This implements a Qt Model class.
    Column definitions:
      See Columns enumerations in image.py and selection.py.
    """

    # These signals are used start long running operations in the background. They are connected to slots in the
    # ModelWorker class, which lives inside another QThread.
    open_command_line_given_images = pyqtSignal()
    open_images = pyqtSignal(list)
    save_and_close_all_images = pyqtSignal()
    close_image = pyqtSignal(QModelIndex, bool)  # boolean parameter: True: save selections to files, False: discard
    save_and_close_all_finished = pyqtSignal()

    def __init__(self, args: Namespace, parent: QObject = None):
        """

        :param args: Parsed command line arguments. Expects an argparse.Namespace object
        :param parent: Optional parent object
        """
        super(Model, self).__init__(parent)
        self.args: Namespace = args
        logger.info(f"Creating Model instance. Arguments: {args}")
        self.worker, self.worker_thread = self._setup_worker_thread()

        # The predefined selections is a list of selections given on the command line. These selections are
        # automatically added to each Image file
        logger.info("Loading selections given on the command line")
        self.predefined_selections: typing.List[SelectionPreset] = self._create_selections_from_command_line()
        logger.debug(f"Loaded selections: {self.predefined_selections}")
        # Load all given images
        self.images: typing.List[Image] = []
        # Wait some milliseconds after the main event loop started and then fill the model in the background.
        # This loads the images in a separate thread and does not block the GUI thread
        QTimer.singleShot(100, self.open_command_line_given_images.emit)

    def _setup_worker_thread(self) -> typing.Tuple[ModelWorker, QThread]:
        """
        Create the worker thread used to perform long running operations in the background.
        """
        worker = ModelWorker(self)
        worker_thread = QThread(self)
        worker_thread.setObjectName("AsynchronousImageWorker")
        worker.moveToThread(worker_thread)
        logger.debug("Created worker thread.")
        self.open_command_line_given_images.connect(worker.open_command_line_given_images)
        self.open_images.connect(worker.open_images)
        self.save_and_close_all_images.connect(worker.save_and_close_all_images)
        self.close_image.connect(worker.close_image)
        logger.debug("Connected signals to offload to the worker thread.")
        worker_thread.start()

        return worker, worker_thread

    def _create_selections_from_command_line(self):
        """Read all selection presets given on the command line."""
        return [SelectionPreset(*selection) for selection in self.args.selections]

    def _open_command_line_given_images(self):
        """
        Open all images given as command line arguments.
        This automatically adds the selections predefined on the command line to each image file.
        """
        logger.info("Loading images given on the command line")
        for image_path_str in self.args.images:
            if self.worker_thread.isInterruptionRequested():
                logger.warning("Requested worker thread interruption. Aborting file loading.")
                break
            image_path = pathlib.Path(image_path_str).expanduser().resolve()
            logger.debug(f"Create Image instance with Path: '{image_path}'")
            self._open_image(image_path)

    def _open_images(self, path_list: typing.Iterable[pathlib.Path]):
        """
        Open a list of image files. This function is used by the file open dialog, because it returns a list with
        selected files.
        """
        for image_path in path_list:
            self._open_image(image_path)

    def add_selection(self, index: QModelIndex, selection: Selection):
        """
        Add a selection to the referenced image.
        """
        image = self.images[index.row()]
        self.beginInsertRows(index, len(image.selections), len(image.selections))
        image.selections.append(selection)
        self.endInsertRows()

    def _open_image(self, path: pathlib.Path):
        """
        Open the image with the given path.
        This automatically adds the selections predefined on the command line to the given image file.
        """
        self.beginInsertRows(QModelIndex(), len(self.images), len(self.images))
        image = Image(path)  # Don’t set the parent yet. See below.
        logger.debug(f"Image instance created. Adding predefined selections as given on the command line: "
                     f"{self.predefined_selections}")
        for selection in self.predefined_selections:
            image.add_selection(selection.to_rectangle(image))
        self.images.append(image)
        image.clear_image_data()
        # Image currently belongs to the self.worker_thread that created it.
        # Move to the main thread, before assigning the parent object, because setting the parent across different
        # threads is unsupported.
        image.moveToThread(self.thread())
        image.setParent(self)
        self.endInsertRows()

    def _save_and_close_all_images(self):
        """
        Save and close all images. This writes all selections to separate files, then closes all files.
        """
        logger.info("Writing all selections and closing all opened image files.")
        for index, image in enumerate(self.images):
            logger.debug(f"Writing output files for {image}")
            self.beginRemoveRows(QModelIndex(), index, index)
            image.write_output()
            self.endRemoveRows()
        self.images.clear()
        self.save_and_close_all_finished.emit()

    def _close_image(self, model_index: QModelIndex, save_selections: bool = True):
        """
        Optionally save and then close a single image file.
        :param model_index: QModelIndex pointing to an Image instance.
        :param save_selections: True: Save all selections to files. False: Discard all selections. Don’t write anything.
        """
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
            logger.debug("No index. Returning invalid QModelIndex()")
            return QModelIndex()

        if parent.isValid():
            parent_item = parent.internalPointer().child(row)
        else:
            # Invalid parent means top level access. Look up the Image in the images list.
            parent_item = self.images[row] if 0 <= row < len(self.images) else None  # Sanity check the row value
        if parent_item is not None:
            return self.createIndex(row, column, parent_item)
        else:
            return QModelIndex()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Qt Model API function. Returns the number of rows/children for the given parent."""
        if not parent.isValid():
            return len(self.images)
        else:
            return parent.internalPointer().row_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Qt Model API function. Returns the number of colums/data items for the given parent."""
        if parent.isValid():
            return parent.internalPointer().column_count()
        else:
            # Invalid indices should return the column count of the root item, which is set to be the Image class
            # column count.
            return Image.column_count()

    def parent(self, child: QModelIndex) -> QModelIndex:
        """Qt Model API function."""
        if not child.isValid():
            return QModelIndex()
        child_item = child.internalPointer()
        parent = child_item.parent()

        if parent is self:
            # Image instances have this as a parent, thus it is a top level access. Thus, there is no parent
            return QModelIndex()
        else:
            return self.createIndex(parent.row(), ImageColumns.IMAGE, parent)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        if not index.isValid():
            return QVariant()
        item = index.internalPointer()
        # Delegate to the model instance data() method
        return item.data(index.column(), role)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        """
        Qt Model API function. Returns the data used for table header display.
        Because the model tree is non-uniform with different classes and column meanings on different nesting levels,
        this doesn’t work well. The data here only represents the top level Image class.
        Proper table display for Selections needs another proxy model, because Qt does not support variable header data
        based on nesting depth / model indices.
        """
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == ImageColumns.IMAGE:
                return "Image"
            elif section == ImageColumns.IMAGE_PATH:
                return "Image path"
            elif section == ImageColumns.OUTPUT_PATH:
                return "Output path"
        return QVariant()
