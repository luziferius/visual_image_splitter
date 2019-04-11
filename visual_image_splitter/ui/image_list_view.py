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

from PyQt5.QtWidgets import QListView, QWidget


from .image_list_delegate import ImageListItemDelegate
from .selection_list_delegate import SelectionListItemDelegate
from ._logger import get_logger

logger = get_logger("image_list_view")
__all__ = ["OpenedImageListView", "SelectionListView"]


class OpenedImageListView(QListView):

    def __init__(self, parent: QWidget=None):
        super(OpenedImageListView, self).__init__(parent)
        # QListView.setItemDelegate does not take the object ownership. Save it as a class attribute to prevent it
        # from getting deleted by the garbage collector.
        self._delegate: ImageListItemDelegate = ImageListItemDelegate(self)
        self.setItemDelegate(self._delegate)
        logger.info(f"Created {self.__class__.__name__} instance.")


class SelectionListView(QListView):

    def __init__(self, parent: QWidget=None):
        super(SelectionListView, self).__init__(parent)
        # QListView.setItemDelegate does not take the object ownership. Save it as a class attribute to prevent it
        # from getting deleted by the garbage collector.
        self._delegate: SelectionListItemDelegate = SelectionListItemDelegate(self)
        self.setItemDelegate(self._delegate)
        logger.info(f"Created {self.__class__.__name__} instance.")



