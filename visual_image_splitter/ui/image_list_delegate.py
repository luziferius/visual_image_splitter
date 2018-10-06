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

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QObject, QModelIndex, QAbstractItemModel, pyqtSlot, QSize
from PyQt5.QtWidgets import QWidget, QPushButton, QStyledItemDelegate, QStyleOptionViewItem, QLineEdit, QStyle

from visual_image_splitter.model.image import Image
from .common import inherits_from_ui_file_with_name
from .choose_dir_dialog import OutputDirDialog


class ImageListItemEditor(*inherits_from_ui_file_with_name("image_list_item_editor")):
    """
    This widget implements an Item editor for the opened image view. It is shown by the view class
    whenever item editing is requested. (Usually by double-clicking an item in the view or any other edit trigger).
    """
    def __init__(self, parent: QWidget=None):
        super(ImageListItemEditor, self).__init__(parent)
        self.setupUi()
        self.output_path: Path = None
        self.input_file_path: Path = None
        self.output_path_chooser = OutputDirDialog(self)
        self.output_path_chooser_button: QPushButton
        self.output_path_chooser_button.clicked.connect(self.on_show_directory_chooser)

    @pyqtSlot()
    def on_show_directory_chooser(self):
        """
        Show a directory chooser dialog. If accepted, it will populate the output_path_chooser line edit with
        the selected path.
        """
        if self.output_path_chooser.exec_() == OutputDirDialog.Accepted:
            path_string = self.output_path_chooser.selectedFiles()[0]
            self.output_path_line_edit: QLineEdit
            self.output_path_line_edit.setText(path_string)
            self.output_path = Path(path_string)

    def set_data_from_index(self, index: QModelIndex):
        """Called by the ImageListItemDelegate to populate the editor with model data."""
        image: Image = index.sibling(index.row(), 0).data(Qt.UserRole)
        self.input_file_path = image.image_path
        self.output_path = image.output_path
        self.output_path_line_edit.setText(str(image.output_path))
        self.file_name_label.setText(self.input_file_path.name)
        self.selection_count_label.setText(str(len(image.selections)))


class ImageListItemDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject=None):
        super(ImageListItemDelegate, self).__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex)-> ImageListItemEditor:
        return ImageListItemEditor(parent)

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        if isinstance(index.data(Qt.UserRole), Image):
            self._paint(painter, option, index)
        else:
            super(ImageListItemDelegate, self).paint(painter, option, index)

    def _paint(self, painter: QtGui.QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        self._setup_painter(painter)
        self._paint_selection_highlight(option, painter)
        pass  # now paint the delegate
        painter.restore()

    @staticmethod
    def _setup_painter(painter):
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

    @staticmethod
    def _paint_selection_highlight(option, painter):
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

    def setEditorData(self, editor: ImageListItemEditor, index: QModelIndex):
        editor.set_data_from_index(index)

    def setModelData(self, editor: ImageListItemEditor, model: QAbstractItemModel, index: QModelIndex):
        pass

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(150, 150)

    def updateEditorGeometry(self, editor: ImageListItemEditor, option: QStyleOptionViewItem, index: QModelIndex):
        editor.setGeometry(option.rect)
