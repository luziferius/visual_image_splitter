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
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle


class CustomItemDelegateBase(QStyledItemDelegate):
    """This class contains some common functionality that is used by both list view delegate classes."""
    @staticmethod
    def _setup_painter(painter):
        """Initialize the given QPainter."""
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

    @staticmethod
    def _paint_selection_highlight(option: QStyleOptionViewItem, painter: QtGui.QPainter):
        """Paints the selection highlight. It is painted in the background of each selected item."""
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

    @staticmethod
    def _create_qrect_with_border(source: QRect, border: int) -> QRect:
        """
        Takes a QRect item, copies it and adds a border, by shrinking the input by border pixels on each
        side. In other words: It performs a centered scaling, by reducing the input QRect size by 2*border pixels.
        """
        target = QRect(source)
        target.setRight(target.right() - border)
        target.setLeft(target.left() + border)
        target.setTop(target.top() + border)
        target.setBottom(target.bottom() - border)
        return target
