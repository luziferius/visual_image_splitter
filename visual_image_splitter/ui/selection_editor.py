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

import typing
import enum

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsRectItem
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QRectF, QModelIndex, Qt, QObject, QPointF, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QPen, QColor, QBrush

from visual_image_splitter.model.selection import Selection
from visual_image_splitter.model.point import Point

from visual_image_splitter.logger import get_logger
module_logger = get_logger(__name__)
del get_logger

editor_logger = module_logger.getChild("selection_editor")
scene_logger = module_logger.getChild("selection_scene")


class EditorMode(enum.Enum):
    DRAW_MODE = enum.auto()
    MOVE_MODE = enum.auto()


class SelectionScene(QGraphicsScene):

    selection_drawing_finished = pyqtSignal(QRectF)

    def __init__(self, scene_rect: QRectF, parent: QObject = None):
        super(SelectionScene, self).__init__(scene_rect, parent)
        rectangle_color = QColor(Qt.red)
        self.default_border_pen = QPen(Qt.red, 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        self.default_fill_brush = QBrush(rectangle_color, Qt.BDiagPattern)
        self.new_selection_view: QGraphicsRectItem = None
        self.new_selection_origin: QPointF = None
        self.mode = EditorMode.DRAW_MODE

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if self.mode == EditorMode.DRAW_MODE:
            self._handle_mouse_press_draw_mode(event)
        elif self.mode == EditorMode.MOVE_MODE:
            raise NotImplementedError("Move mode is not implemented!")

    def _handle_mouse_press_draw_mode(self, event: QGraphicsSceneMouseEvent):
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
        if self.mode == EditorMode.DRAW_MODE:
            self._handle_mouse_move_draw_mode(event)
        elif self.mode == EditorMode.MOVE_MODE:
            raise NotImplementedError("Move mode is not implemented!")

    def _handle_mouse_move_draw_mode(self, event: QGraphicsSceneMouseEvent):
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
        if self.mode == EditorMode.DRAW_MODE:
            self._handle_mouse_release_draw_mode(event)
        elif self.mode == EditorMode.MOVE_MODE:
            raise NotImplementedError("Move mode is not implemented!")

    def _handle_mouse_release_draw_mode(self, event: QGraphicsSceneMouseEvent):
        self.new_selection_view: QGraphicsRectItem
        if event.button() == Qt.LeftButton and self.new_selection_view is not None:
            absolute_rectangle = self.new_selection_view.mapRectFromScene(self.new_selection_view.rect())
            if self.is_rectangle_valid_selection(absolute_rectangle):
                self.selection_drawing_finished.emit(absolute_rectangle)
            else:
                scene_logger.info(
                    f"Discarding invalid selection: "
                    f"x={absolute_rectangle.x()}, y={absolute_rectangle.y()}, "
                    f"width={absolute_rectangle.width()}, height={absolute_rectangle.height()}"
                )
                self.removeItem(self.new_selection_view)
            self.new_selection_origin = None
            self.new_selection_view = None
            event.accept()

    def load_selections(self, current: QModelIndex):
        selection_count: int = current.model().rowCount(current)  # The number of child nodes, which are selections
        current_first_column = current.sibling(current.row(), 0)  # Selections are below the first column
        selections: typing.List[Selection] = [
            current_first_column.child(index, 0).data(Qt.UserRole) for index in range(selection_count)
        ]
        editor_logger.debug(f"Loading selection list: {selections}")
        for selection in selections:
            self._draw_rectangle(current, selection)

    def _restrict_to_scene_space(self, point: QPointF):
        """Restrict rectangle drawing to the screen space. This prevents drawing out of the source image bounds."""
        point.setX(min(max(point.x(), 0), self.sceneRect().width()))
        point.setY(min(max(point.y(), 0), self.sceneRect().height()))

    def _draw_rectangle(self, current: QModelIndex, rectangle: Selection):
        self.addRect(
            self._to_local_coordinates(current, rectangle),
            self.default_border_pen,
            self.default_fill_brush
        )

    def _to_local_coordinates(self, current: QModelIndex, rectangle: Selection) -> QRectF:
        """
        Scales a model Selection to local coordinates. Large images are scaled down, so the rectangles need to be
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

    def is_rectangle_valid_selection(self, selection: QRectF) -> bool:
        """
        Returns True, if the given rectangle is a valid selection.
        A selection is determined to be valid if its width and height is at least 0.5% of the source image or 20 pixels
        large, whichever comes first
        """
        return (selection.width() > self.sceneRect().width() * 0.01 or selection.width() > 20) \
            and (selection.height() > self.sceneRect().height() * 0.01 or selection.height() > 20)


class SelectionEditor(QGraphicsView):

    def __init__(self, parent: QWidget = None):
        super(SelectionEditor, self).__init__(parent)

    @pyqtSlot(QModelIndex, QModelIndex)
    def on_active_image_changed(self, current: QModelIndex, previous: QModelIndex):
        """
        Called, whenever the selected image changes.
        This happens, when the user clicks on an image in the opened images list to edit the selections.
        """
        if current.isValid():
            data = current.data(Qt.BackgroundRole)
            if data is not None:
                self.load_image(data)
                self.load_selections(current)
            else:
                editor_logger.info(f"Invalid index {current}. row={current.row()}, column={current.column()}")
        else:
            editor_logger.debug("Selection changed to an invalid index. Clearing scene.")
            self.clear()

    def load_image(self, image: QPixmap):
        new_scene = SelectionScene(QRectF(image.rect()), parent=self)
        new_scene.addPixmap(image)
        editor_logger.info(f"Loaded scene: image-dimensions={image.rect().width(), image.rect().height()}")
        self._replace_scene(new_scene)
        new_scene.selection_drawing_finished.connect(self.on_selection_drawing_finished)

    def on_selection_drawing_finished(self, local_rectangle: QRectF):
        image_index: QModelIndex = QApplication.instance().get_currently_edited_image()
        model = QApplication.instance().model
        model.add_selection(image_index, self._from_local_coordinates(image_index, local_rectangle))
        editor_logger.info(f"Selection drawing finished: width={local_rectangle.width()}, height={local_rectangle.height()}")

    @pyqtSlot()
    def clear(self):
        self._replace_scene(QGraphicsScene(self))
        editor_logger.info("Cleared currently opened scene")

    def _replace_scene(self, new_scene: QGraphicsScene):
        # TODO: Must the old scene be destroyed manually or is this ok? Then this setter can be removed
        self.setScene(new_scene)

    def load_selections(self, current: QModelIndex):
        self.scene().load_selections(current)

    def _from_local_coordinates(self, image_index: QModelIndex, rectangle: QRectF) -> Selection:
        """
        Scales a floating point rectangle from local coordinates to an integer based rectangle in the source image
        coordinates.
        """
        image = image_index.sibling(image_index.row(), 0).data(Qt.UserRole)
        image_width: int = image.width
        scaling_factor = image_width / self.scene().width()

        return Selection(
            Point(
                round(rectangle.left()*scaling_factor),
                round(rectangle.top()*scaling_factor)),
            Point(
                round(rectangle.right()*scaling_factor),
                round(rectangle.bottom()*scaling_factor)),
            image
        )
