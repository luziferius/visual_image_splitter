# Copyright (C) 2018, 2019 Thomas Hess <thomas.hess@udo.edu>

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


from PyQt5.QtCore import pyqtSlot, pyqtSignal, QModelIndex
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget, QApplication

from visual_image_splitter.ui.common import inherits_from_ui_file_with_name
from visual_image_splitter.ui.selection_editor import SelectionEditor
from visual_image_splitter.ui.list_views import OpenedImageListView, SelectionListView
from visual_image_splitter.ui.open_images_dialog import OpenImagesDialog
from visual_image_splitter.logger import get_logger
logger = get_logger(__name__)
del get_logger


class MainWindow(*inherits_from_ui_file_with_name("main_window")):

    open_command_line_given_images = pyqtSignal()
    open_images = pyqtSignal(list)
    close_image = pyqtSignal(QModelIndex, bool)

    def __init__(self, model, parent: QWidget = None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.dirty: bool = False
        self.image_view: SelectionEditor
        self.opened_images_list_view: OpenedImageListView
        self.opened_images_list_view.setModel(model)
        self.selection_list_view: SelectionListView
        self.selection_list_view.setModel(model)
        self.selection_list_view.clear_list()
        self.opened_images_list_view.selectionModel().currentRowChanged.connect(
            self.image_view.on_active_image_changed
        )
        self.opened_images_list_view.selectionModel().currentRowChanged.connect(
            self.selection_list_view.on_active_image_changed
        )
        logger.info(f"Created {self.__class__.__name__} instance.")
        self._connect_model_signals(model)

    def _connect_model_signals(self, model):
        """Connect all GUI actions with the model."""
        self.open_images.connect(model.open_images)
        model.save_and_close_all_finished.connect(self.image_view.clear)
        model.save_and_close_all_finished.connect(self.selection_list_view.clear_list)
        self.action_save_all.triggered.connect(model.save_and_close_all_images)
        self.action_save_current.triggered.connect(self.selection_list_view.clear_list)
        self.action_save_current.triggered.connect(self.image_view.clear)
        self.action_close_current.triggered.connect(self.selection_list_view.clear_list)
        self.action_close_current.triggered.connect(self.image_view.clear)
        self.close_image.connect(model.close_image)

        logger.debug("Connected action signals with model signals")

    def closeEvent(self, event: QCloseEvent):
        """
        This function is automatically called when the window is closed using the close [X] button in the window
        decorations or by right clicking in the system window list and using the close action, or similar ways to close
        the window.
        Just ignore this event and simulate that the user used the action_quit instead.

        To quote the Qt5 QCloseEvent documentation: If you do not want your widget to be hidden, or want some special
        handling, you should reimplement the event handler and ignore() the event.
        """
        event.ignore()
        # Be safe and emit this signal, because it might be connected to multiple slots.
        self.action_quit.triggered.emit()

    @pyqtSlot()
    def on_action_quit_triggered(self):
        if self.dirty:
            # TODO: Unsaved changes. Ask the user what to do: Save and exit, Discard and exit, or keep running?
            pass
        # Prevent a loop, because shutdown() closes this window, causing closeEvent to fire, in turn causing this to be
        # called again. So just disconnect the signal. The connection won’t be needed during application shutdown.
        self.action_quit.triggered.disconnect(self.on_action_quit_triggered)
        QApplication.instance().shutdown()

    @pyqtSlot()
    def on_action_open_triggered(self):
        open_images_dialog = OpenImagesDialog(self)
        if open_images_dialog.exec_() == OpenImagesDialog.Accepted:
            paths = open_images_dialog.selected_paths()
            logger.debug(f"File open dialog accepted. Emitting open_images signal with paths={paths}")
            self.open_images.emit(paths)

    @pyqtSlot()
    def on_action_save_current_triggered(self):
        selected_image = self.opened_images_list_view.selectionModel().currentIndex()
        self.close_image.emit(selected_image, True)

    @pyqtSlot()
    def on_action_close_current_triggered(self):
        selected_image = self.opened_images_list_view.selectionModel().currentIndex()
        self.close_image.emit(selected_image, False)
