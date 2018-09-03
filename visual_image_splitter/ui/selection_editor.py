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

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsRectItem
from PyQt5.QtCore import QRectF, QRect, QModelIndex, Qt, QObject, QPointF
from PyQt5.QtGui import QPixmap, QPen, QColor, QBrush

from visual_image_splitter.model.rectangle import Rectangle

from ._logger import get_logger
logger = get_logger("selection_editor")
scene_logger = get_logger("selection_scene")


class SelectionScene(QGraphicsScene):

    def __init__(self, scene_rect: QRectF, parent: QObject=None):
        super(SelectionScene, self).__init__(scene_rect, parent)
        rectangle_color = QColor(Qt.red)
        self.default_border_pen = QPen(Qt.red, 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        self.default_fill_brush = QBrush(rectangle_color, Qt.BDiagPattern)
        self.new_selection_view: QGraphicsRectItem = None
        self.new_selection_origin: QPointF = None

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton and self.new_selection_view is None:
            self.new_selection_origin = event.scenePos()
            self._restrict_to_scene_space(self.new_selection_origin)
            scene_logger.info(
                f"Beginning to draw a new selection: "
                f"X={self.new_selection_origin.x()}, Y={self.new_selection_origin.y()}"
            )
            self.new_selection_view = QGraphicsRectItem(
                self.new_selection_origin.x(), self.new_selection_origin.y(), 0, 0
            )
            self.new_selection_view.setPen(self.default_border_pen)
            self.new_selection_view.setBrush(self.default_fill_brush)
            self.addItem(self.new_selection_view)
            event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        point2 = event.scenePos()
        self._restrict_to_scene_space(point2)
        if self.new_selection_origin is None:
            scene_logger.warning("Move event: Selection origin is None!")
            event.accept()
            return

        rectangle = QRectF(
            QPointF(min(self.new_selection_origin.x(), point2.x()), min(self.new_selection_origin.y(), point2.y())),
            QPointF(max(self.new_selection_origin.x(), point2.x()), max(self.new_selection_origin.y(), point2.y()))
        )
        self.new_selection_view.setRect(rectangle)
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton and self.new_selection_view is not None:
            # TODO: Instead of discarding the selection, add it to the model. Emit a selection_finished signal?
            self.removeItem(self.new_selection_view)
            self.new_selection_origin = None
            self.new_selection_view = None
            event.accept()

    def load_selections(self, current: QModelIndex):
        selections: typing.List[Rectangle] = current.sibling(current.row(), 1).data(Qt.UserRole)
        for rectangle in selections:
            self._draw_rectangle(current, rectangle)

    def _restrict_to_scene_space(self, point: QPointF):
        point.setX(min(max(point.x(), 0), self.sceneRect().width()))
        point.setY(min(max(point.y(), 0), self.sceneRect().height()))

    def _draw_rectangle(self, current: QModelIndex, rectangle: Rectangle):
        self.addRect(
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
        scaling_factor: float = self.width() / current.sibling(current.row(), 0).data(Qt.UserRole).width

        if scaling_factor >= 1:
            result = rectangle.as_qrectf
        else:
            result = QRectF(
                rectangle.top_left.x*scaling_factor,
                rectangle.top_left.y*scaling_factor,
                rectangle.width*scaling_factor,
                rectangle.height*scaling_factor
            )
            scene_logger.debug(f"Scaled {rectangle} to {result.topLeft(), result.bottomRight()}")
        return result

    def _from_local_coordinates(self, rectangle: QRectF) -> QRect:
        """
        Scales a floating point rectangle from local coordinates to an integer based rectangle in the source image
        coordinates.
        """
        pass


class SelectionEditor(QGraphicsView):

    def on_image_selection_changed(self, current: QModelIndex, previous: QModelIndex):
        """
        Called, whenever the selected image changes.
        This happens, when the user clicks on an image in the opened images list to edit the selections.
        """
        del previous  # Currently not used signal parameter.
        if current.isValid():
            logger.debug(f"Selected: {current}, column={current.column()}, row={current.row()}")
            data = current.data(Qt.BackgroundRole)
            if data is not None:
                self.load_image(data)
            self.load_selections(current)
        else:
            logger.debug("Selection changed to an invalid index. Clearing scene.")
            self.clear()

    def load_image(self, image: QPixmap):
        new_scene = SelectionScene(QRectF(image.rect()), parent=self)
        new_scene.addPixmap(image)
        logger.info(f"Loaded scene: image-dimensions={image.rect().width(), image.rect().height()}")
        self._replace_scene(new_scene)

    def clear(self):
        self._replace_scene(QGraphicsScene(self))
        logger.info("Cleared currently opened scene")

    def _replace_scene(self, new_scene: QGraphicsScene):
        # TODO: Must the old scene be destroyed manually or is this ok? Then this setter can be removed
        self.setScene(new_scene)

    def load_selections(self, current: QModelIndex):
        self.scene().load_selections(current)
