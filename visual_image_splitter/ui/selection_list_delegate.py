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


from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel, QSize, QRect
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem

from visual_image_splitter.model.selection import Selection
from .custom_image_delegate_base import CustomItemDelegateBase


class SelectionListItemDelegate(CustomItemDelegateBase):
    """This class renders Selections inside the selection list view."""

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        return QWidget(parent)

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        if isinstance(index.data(Qt.UserRole), Selection):
            SelectionListItemDelegate._paint(painter, option, index)
        else:
            super(SelectionListItemDelegate, self).paint(painter, option, index)

    @staticmethod
    def _paint(painter: QtGui.QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        SelectionListItemDelegate._setup_painter(painter)
        SelectionListItemDelegate._paint_selection_highlight(option, painter)
        SelectionListItemDelegate._paint_selection_image(painter, option, index)
        painter.restore()

    @staticmethod
    def _paint_selection_image(painter: QtGui.QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        selection: Selection = index.data(Qt.UserRole)
        image_region = SelectionListItemDelegate._scale_image(selection, option)
        painter.drawPixmap(image_region, selection.thumbnail)

    @staticmethod
    def _scale_image(selection: Selection, option: QStyleOptionViewItem) -> QRect:
        source_aspect_ratio = selection.width / selection.height
        target_image_region = SelectionListItemDelegate._create_qrect_with_border(option.rect, 4)
        target_image_region.setWidth(round(target_image_region.height() * source_aspect_ratio))

        return target_image_region

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        pass

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        pass

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        return QSize(150, 150)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor.setGeometry(option.rect)
