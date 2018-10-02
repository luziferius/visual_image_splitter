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


from PyQt5.QtCore import pyqtSlot, pyqtSignal, QModelIndex
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget, QApplication, QTreeView

from visual_image_splitter.ui.common import inherits_from_ui_file_with_name
from visual_image_splitter.ui.selection_editor import SelectionEditor
from visual_image_splitter.ui._logger import get_logger
from visual_image_splitter.ui.open_images_dialog import OpenImagesDialog

logger = get_logger("main_window")


class MainWindow(*inherits_from_ui_file_with_name("main_window")):

    open_command_line_given_images = pyqtSignal()
    open_images = pyqtSignal(list)
    close_image = pyqtSignal(QModelIndex, bool)

    def __init__(self, model, parent: QWidget=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.dirty: bool = False
        self.image_view: SelectionEditor
        self.opened_images_table_view: QTreeView
        self.opened_images_table_view.setModel(model)
        self.opened_images_table_view.selectionModel().currentChanged.connect(self.image_view.on_image_selection_changed)
        self.selection_table_view: QTreeView
        self.selection_table_view.setModel(model)
        self.selection_table_view.setRootIndex(QModelIndex())
        self.opened_images_table_view.selectionModel().currentChanged.connect(lambda current, last: self.selection_table_view.setRootIndex(current))
        logger.info("Created main window instance")
        self._connect_model_signals(model)

    def _connect_model_signals(self, model):
        self.open_images.connect(model.open_images)
        self.action_save_all.triggered.connect(model.save_and_close_all_images)
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
