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

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import QRectF, QModelIndex, Qt
from PyQt5.QtGui import QPixmap

from ._logger import get_logger
logger = get_logger("selection_editor")


class SelectionEditor(QGraphicsView):

    def on_image_selection_changed(self, current: QModelIndex, previous: QModelIndex):
        """
        Called, whenever the selected image changes.
        This happens, when the user clicks on an image in the opened images list to edit the selections.
        """
        if current.isValid():
            logger.debug(f"Selected: {current}, column={current.column()}, row={current.row()}")
            data = current.data(Qt.BackgroundRole)
            if data is not None:
                self.load_image(data)

    def load_image(self, image: QPixmap):
        new_scene = QGraphicsScene(QRectF(image.rect()), parent=self)
        new_scene.addPixmap(image)
        logger.info(f"Loaded scene: image-dimensions={image.rect().width(), image.rect().height()}")
        self.setScene(new_scene)

