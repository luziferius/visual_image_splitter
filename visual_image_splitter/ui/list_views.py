# Copyright (C) 2019 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtCore import pyqtSlot, QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QListView, QWidget


from visual_image_splitter.model.model import Model
from .image_list_delegate import ImageListItemDelegate
from .selection_list_delegate import SelectionListItemDelegate
from visual_image_splitter.logger import get_logger
logger = get_logger(__name__)
del get_logger
__all__ = ["OpenedImageListView", "SelectionListView"]


class OpenedImageListView(QListView):

    def __init__(self, parent: QWidget = None):
        super(OpenedImageListView, self).__init__(parent)
        # QListView.setItemDelegate does not take the object ownership. Save it as a class attribute to prevent it
        # from getting deleted by the garbage collector.
        self._delegate: ImageListItemDelegate = ImageListItemDelegate(self)
        self.setItemDelegate(self._delegate)
        logger.info(f"Created {self.__class__.__name__} instance.")


class SelectionListView(QListView):

    def __init__(self, parent: QWidget = None):
        super(SelectionListView, self).__init__(parent)
        # QListView.setItemDelegate does not take the object ownership. Save it as a class attribute to prevent it
        # from getting deleted by the garbage collector.
        self._delegate: SelectionListItemDelegate = SelectionListItemDelegate(self)
        self.setItemDelegate(self._delegate)
        self._model: Model = None
        logger.info(f"Created {self.__class__.__name__} instance.")

    def setModel(self, model: QAbstractItemModel):
        self._model = model
        super(SelectionListView, self).setModel(model)

    @pyqtSlot(QModelIndex, QModelIndex)
    def on_active_image_changed(self, current: QModelIndex, previous: QModelIndex):
        """
        This slot gets called, if the currently active image changes. The function updates the root index,
        so that the list view shows the selections for the newly active image.
        """
        logger.debug(f"Selection changed. "
                     f"current: isValid={current.isValid()}, column={current.column()}, row={current.row()}; "
                     f"previous: isValid={previous.isValid()}, column={previous.column()}, row={previous.row()}")
        # Be safe and map all indices to the first column.
        if current.column():
            current = current.sibling(current.row(), 0)
        if self.model() is None:
            super(SelectionListView, self).setModel(self._model)
        if current.isValid():
            super(SelectionListView, self).setRootIndex(current)

    @pyqtSlot()
    def clear_list(self):
        """Temporarily remove the set model. This causes the view to clear. It is called, whenever there is no active
        image. This happens, if the current image is closed or saved or if all images are saved."""
        super(SelectionListView, self).setModel(None)
