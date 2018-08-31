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

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget
from PyQt5.QtCore import QRectF, QRect, QModelIndex, Qt
from PyQt5.QtGui import QPixmap, QPen, QColor, QBrush

from visual_image_splitter.model.rectangle import Rectangle
from visual_image_splitter.model.image import Image

from ._logger import get_logger
logger = get_logger("selection_editor")


class SelectionEditor(QGraphicsView):

    def __init__(self, parent: QWidget=None):
        super(SelectionEditor, self).__init__(parent)
        rectangle_color = QColor(Qt.red)
        self.default_border_pen = QPen(Qt.red, 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        self.default_fill_brush = QBrush(rectangle_color, Qt.BDiagPattern)

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
            self.load_selections(current)

    def load_image(self, image: QPixmap):
        new_scene = QGraphicsScene(QRectF(image.rect()), parent=self)
        new_scene.addPixmap(image)
        logger.info(f"Loaded scene: image-dimensions={image.rect().width(), image.rect().height()}")
        self.setScene(new_scene)

    def load_selections(self, current: QModelIndex):
        selections: typing.List[Rectangle] = current.sibling(current.row(), 1).data(Qt.UserRole)
        for rectangle in selections:
            self._draw_rectangle(current, rectangle)

    def _draw_rectangle(self, current: QModelIndex, rectangle: Rectangle):
        self.scene().addRect(
            self._to_local_coordinates(current, rectangle),
            self.default_border_pen,
            self.default_fill_brush
        )

    def _to_local_coordinates(self, current: QModelIndex, rectangle: Rectangle) -> QRectF:
        """
        Scales a model rectangle to local coordinates. Large images are scaled down, so the rectangles need to be
        scaled, too. This function performs the scaling and conversion to floating point based rectangles, as expected
        by QGraphicsView.
        """
        scaling_factor: float = self.scene().width() / current.sibling(current.row(), 0).data(Qt.UserRole).width

        if scaling_factor >= 1:
            result = QRectF(rectangle.as_qrect())
        else:
            result = QRectF(
                rectangle.top_left.x*scaling_factor,
                rectangle.top_left.y*scaling_factor,
                rectangle.width*scaling_factor,
                rectangle.height*scaling_factor
            )
            logger.debug(f"Scaled {rectangle} to {result.topLeft(), result.bottomRight()}")
        return result

    def _from_local_coordinates(self, rectangle: QRectF) -> QRect:
        """
        Scales a floating point rectangle from local coordinates to an integer based rectangle in the source image
        coordinates.
        """
        pass
