from PySide6.QtWidgets import (QGraphicsItem,
                               QGraphicsScene,
                               QGraphicsSceneMouseEvent,
                               QGraphicsView,
                               QMenu,
                               QStyleOptionGraphicsItem,
                               QVBoxLayout,
                               QWidget)
from PySide6.QtCore import Signal, Qt, QRect, QPoint, QRectF, QPointF
from PySide6.QtGui import QPainter, QFont, QBrush, QColor, QFontMetrics, QPen, QAction, QWheelEvent
from typing import Self, Optional

from episcope.localization import I18N
from episcope.core import Timeline, Symptom, Attribute

# The maximum level of zoom (zoom in).
MAX_ZOOM_UNIT = 0.3
# Default zoom-level.
DEFAULT_ZOOM_UNIT = 0.011

# The height of the cursor section. Timeline starts after this.
LINE_START_PX = 20
# Height of a line in the timeline.
LINE_HEIGHT_PX = 50
# Width of the timeline cursor.
CURSOR_WIDTH_PX = 20
# Minimum size of a step(gradation) on the timeline.
MIN_TIMELINE_STEP_WIDTH_PX = 20

# Default duration of the newly created symptoms. 10s by default.
SYMPTOM_DEFAULT_DURATION_MS = 10 * 1000

# Default font size for the timeline
DEFAULT_FONT_SIZE = 10
# Default font name.
DEFAULT_FONT_NAME = "arial"

class TimelineElement(QGraphicsItem):
    def __init__(self, x, y, width, height, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        self._width = width;
        self._height = height;
        self._x = x
        self._y = y
        self._offset = 0
        self._unit = DEFAULT_ZOOM_UNIT

    def _onSizeChanged(self : Self) -> None:
        pass

    def width(self : Self) -> float:
        return self._width * self._unit

    def rawWidth(self : Self) -> float:
        return self._width

    def height(self : Self) -> float:
        return self._height

    def setWidth(self, width):
        self._width = width / self._unit
        self._onSizeChanged()

    def setRawWidth(self, width):
        self._width = width
        self._onSizeChanged()

    def setHeight(self, height):
        self._height = height
        self._onSizeChanged()

    def x(self):
        return self._x * self._unit - self._offset

    def rawX(self):
        return self._x

    def y(self):
        return self._y

    def setX(self, x):
        self._x = (x + self._offset) / self._unit

    def setRawX(self, x):
        self._x = x

    def setUnit(self, unit):
        self._unit = unit
        self._onSizeChanged()

    def setOffset(self, offset):
        self._offset = offset

    def boundingRect(self):
        return QRectF(self.x(), self.y(), self.width(), self.height())

    def grabbedLeftHandle(self, x):
        return False

    def grabbedRightHandle(self, x):
        return False

    def intersects(self, x, y):
        if y < self.y() or y > self.y() + self.height():
            return False
        if x < self.x() or x > self.x() + self.width():
            return False
        return True

class TimelineBlock(TimelineElement):
    HANDLE_WIDTH = 6
    HANDLE_MARGIN = 3
    HANDLE_CUTOFF = 20
    FONT = QFont(DEFAULT_FONT_NAME, DEFAULT_FONT_SIZE)
    FONT_METRIC = QFontMetrics(FONT)

    def __init__(self, symptom, x, width, *kargs, **kwargs):
        super().__init__(x, LINE_START_PX, width, LINE_HEIGHT_PX, *kargs, **kwargs)
        self._line = 0
        self._symptom = symptom
        self._computeText()

    def symptom(self : Self) -> Symptom:
        return self._symptom

    def _onSizeChanged(self : Self) -> None:
        self._computeText()

    # Override of the base class y(): block's height depends on its line.
    def y(self):
        return LINE_START_PX + self.line() * LINE_HEIGHT_PX

    def line(self):
        return self._line

    def setLine(self, line):
        self._line = line

    def _canDrawHandles(self : Self) -> bool:
        return self.width() >= self.HANDLE_CUTOFF

    def _handlesSize(self : Self) -> int:
        return 0 if not self._canDrawHandles() else self.HANDLE_WIDTH + self.HANDLE_MARGIN

    def _availableSpaceForText(self : Self) -> int:
        return int(self.width() - self._handlesSize())

    # Compute the text that can be shown in the block
    def _computeText(self : Self) -> None:
        self._text = ""
        self._textWidth = 0

        letter_width = self.FONT_METRIC.horizontalAdvance("A")
        available = self._availableSpaceForText()
        letter_count = int(available // letter_width)

        if letter_count < 3:
            return

        name = self._symptom.name
        self._text = name[:min(letter_count, len(name))]
        self._textWidth = self.FONT_METRIC.horizontalAdvance(self._text)

    def _drawHandle(self, painter, x):
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(QColor.fromRgb(42, 96, 135))
        painter.setBrush(brush)

        # Draw outter shape
        height = self.height() - 2 * self.HANDLE_MARGIN
        painter.drawRoundedRect(QRect(x, self.y() + self.HANDLE_MARGIN, self.HANDLE_WIDTH, height), 2, 2)

        # Draw inner shape
        brush.setColor(QColor.fromRgb(81, 176, 245))
        painter.setBrush(brush)
        painter.drawRoundedRect(QRect(x + 2, self.y() + self.height() / 2 - 5, 2, 10), 2, 2)

    def _drawBackground(self, painter):
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(QColor.fromRgb(81, 176, 245))
        painter.setBrush(brush)
        painter.drawRoundedRect(QRect(self.x(), self.y(), self.width(), self.height()), 2, 2)

    def _drawText(self : Self, painter : QPainter, availableSpace : int) -> None:
        if self._textWidth == 0:
            return
        painter.setPen(Qt.black)
        painter.setFont(self.FONT)
        y = self.y() + self.height() / 2 + self.FONT_METRIC.height() / 4
        x = self.x() + self.width() / 2 - self._textWidth / 2
        painter.drawText(QPoint(x, y), self._text);
        painter.setPen(Qt.NoPen)

    def paint(self, painter, option, widget=None):
        painter.setPen(Qt.NoPen)
        self._drawBackground(painter)

        draw_handles = self._canDrawHandles()
        handle_size = self._handlesSize()
        self._drawText(painter, self.width() - handle_size * 2)
        if draw_handles:
            handle_left_x = self.HANDLE_MARGIN
            handle_right_x = self.width() - self.HANDLE_WIDTH - self.HANDLE_MARGIN
            self._drawHandle(painter, self.x() + handle_left_x)
            self._drawHandle(painter, self.x() + handle_right_x)

    def grabbedLeftHandle(self, x):
        if self.width() < self.HANDLE_CUTOFF:
            return False
        return x <= self.x() + self.HANDLE_WIDTH + self.HANDLE_MARGIN

    def grabbedRightHandle(self, x):
        if self.width() < self.HANDLE_CUTOFF:
            return False
        return x >= self.x() + self.width() - self.HANDLE_WIDTH - self.HANDLE_MARGIN

class TimelineBackground(QGraphicsItem):
    def __init__(self, width, height, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        self._width = width;
        self._height = height;
        self._unit = DEFAULT_ZOOM_UNIT
        self._offset = 0
        self._computeDrawingConstants()
        self._media_duration = None

    def setOffset(self, offset):
        self._offset = offset
        self._computeDrawingConstants()

    def setUnit(self, unit):
        self._unit = unit
        self._computeDrawingConstants()

    def setMediaDuration(self, duration):
        self._media_duration = duration
        self._computeDrawingConstants()

    def resize(self, width, height):
        self._width = width
        self._height = height
        self._computeDrawingConstants()

    def _computeDrawingConstants(self):
        if self._width < 10:
            return
        msPerChunk = 2
        pxPerChunk = 0
        while pxPerChunk < MIN_TIMELINE_STEP_WIDTH_PX:
            msPerChunk *= 4
            msPerWidth = self._width / self._unit
            chunkCount = msPerWidth / msPerChunk
            pxPerChunk = self._width / chunkCount

        self._x_start = -pxPerChunk * ((self._offset / self._unit) % msPerChunk / msPerChunk)
        self._x_end = self._width
        if self._media_duration is not None:
            self._x_end = self._media_duration * self._unit - self._offset
        self._pxPerChunk = pxPerChunk
        self._chunkCount = int(self._width / pxPerChunk + 1)

    def paint(self, painter, option, widget=None):
        pen = QPen(QColor.fromRgb(200, 200, 200))
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(QColor.fromRgb(255, 255, 255))

        painter.setPen(pen)
        painter.setBrush(brush)

        for i in range(self._chunkCount):
            x = i * self._pxPerChunk + self._x_start
            painter.drawLine(x, 0, x, self._height)

        pen = QPen(QColor.fromRgb(100, 100, 100))
        painter.setPen(pen)
        for i in range(self._chunkCount):
            x = i * self._pxPerChunk + self._x_start
            painter.drawLine(x + self._pxPerChunk // 2, 0, x + self._pxPerChunk // 2, self._height)

        if self._x_end < self._width:
            brush.setColor(QColor.fromRgb(255, 0, 0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(brush)
            painter.drawRect(self._x_end, 0, self._width, self._height)

class TimelineCursor(TimelineElement):
    def __init__(self, height, *kargs, **kwargs):
        super().__init__(1, 0, CURSOR_WIDTH_PX, height, *kargs, **kwargs)

    def intersects(self, x, y):
        if y > LINE_START_PX:
            return False
        if x < self.x() - CURSOR_WIDTH_PX / 2 or x > self.x() + CURSOR_WIDTH_PX / 2:
            return False
        return True

    def boundingRect(self):
        return QRectF(self.x() - CURSOR_WIDTH_PX / 2, self.y(), CURSOR_WIDTH_PX, self.height())

    def paint(self, painter, option, widget=None):
        painter.setPen(Qt.NoPen)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(QColor.fromRgb(255, 0, 0))
        painter.setBrush(brush)
        painter.drawRect(QRect(self.x() - 1, self.y(), 2, self.height()))
        painter.drawPolygon([
            QPoint(self.x() - CURSOR_WIDTH_PX / 2, self.y()),
            QPoint(self.x() + CURSOR_WIDTH_PX / 2, self.y()),
            QPoint(self.x(), self.y() + LINE_START_PX)])

class DragState():
    def boundingRect(self):
        return QRectF(self.x(), self.y(), self.width(), self.height())

    def __init__(self, start_position, item):
        self._last_position = start_position
        self._item = item
        if self._item is None:
            return

        self._grabbedLeft = self._item.grabbedLeftHandle(start_position.x())
        self._grabbedRight = self._item.grabbedRightHandle(start_position.x())
        # If we grabbed both handles, something is wrong.
        assert(not (self._grabbedLeft == True and self._grabbedRight == True))

    def latchDelta(self, position):
        delta = position - self._last_position
        self._last_position = position
        return delta

    def delta(self, position):
        return position - self._last_position

    def item(self):
        return self._item

    def grabbedLeftHandle(self):
        return self._item is not None and self._grabbedLeft

    def grabbedRightHandle(self):
        return self._item is not None and self._grabbedRight

class TimelineScene(QGraphicsScene):
    on_seek = Signal(int)
    on_symptom_edit = Signal(Symptom)

    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        self._lines = []
        self._lastMouseEvent = None
        self._dragState = None
        self._unit = DEFAULT_ZOOM_UNIT
        self._offset = 0
        self._media_duration = None
        self._windowWidth = 0
        self._windowHeight = 0

        sceneWidth = self.sceneRect().width()
        sceneHeight = self.sceneRect().height()
        self._cursor = TimelineCursor(sceneHeight)
        self._background = TimelineBackground(sceneWidth, sceneHeight)

    def getTimeline(self : Self) -> Timeline:
        timeline = Timeline()
        for line in self._lines:
            for item in line:
                timeline.addSymptom(item.symptom(), int(item.rawX()), int(item.rawX() + item.rawWidth()))
        return timeline

    def getTimelineDuration(self : Self) -> int:
        duration = 0
        for line in self._lines:
            if len(line) == 0:
                continue
            duration = max(duration, line[-1].rawX() + line[-1].rawWidth())
        return duration

    def _sceneHeight(self) -> int:
        return LINE_START_PX + len(self._lines) * LINE_HEIGHT_PX

    def _computeSceneRect(self : Self) -> None:
        # If the scene is larger than the window, scrollbars are shown.
        # - horizontal: we handle that ourselves. Always report the same size.
        # - vertical: we want to use the max space, but allow scrolling.
        rect = QRectF(0, 0, self._windowWidth, max(self._sceneHeight(), self._windowHeight))
        self.setSceneRect(rect)
        self._cursor.setHeight(rect.height())
        self._background.resize(rect.width(), rect.height())
        self._redrawScene()

    def onWindowResize(self, width, height):
        self._windowWidth = width
        self._windowHeight = height
        self._computeSceneRect()

    def _onLineCountChange(self : Self):
        self._computeSceneRect()

    def _minUnit(self : Self) -> None:
        max_time = self.getTimelineDuration() * 2
        if max_time < 1:
            return DEFAULT_ZOOM_UNIT

        if self._media_duration:
            max_time = self._media_duration
        return self._windowWidth / max_time

    def setUnit(self, unit):
        unit = min(MAX_ZOOM_UNIT, max(self._minUnit(), unit))
        self._unit = unit
        for item in self.items():
            item.setUnit(unit)
        self._cursor.setUnit(unit)
        self._background.setUnit(unit)
        self._redrawScene()

    def offset(self):
        return self._offset

    def _maxOffset(self : Self) -> None:
        max_time = self.getTimelineDuration()
        if self._media_duration:
            max_time = self._media_duration
        return max_time * self._unit

    def setOffset(self, offset):
        offset = max(0, min(self._maxOffset(), offset))
        self._offset = offset
        for item in self.items():
            item.setOffset(offset)
        self._cursor.setOffset(offset)
        self._background.setOffset(offset)
        self._redrawScene()

    def _pixelToTime(self : Self, x_px : float) -> int:
        return int(max(0, (x_px + self._offset) / self._unit))

    def _pixelToLine(self : Self, y_px : float) -> int:
        return max(0, int((y_px - LINE_START_PX) / LINE_HEIGHT_PX))

    def _redrawScene(self):
        self.invalidate()

    def defaultBlockDuration(self : Self) -> int:
        return self._pixelToTime(self._windowWidth / 4) - self._pixelToTime(0)

    def drawBackground(self, painter, rect):
        self._background.paint(painter, QStyleOptionGraphicsItem())

    def drawForeground(self, painter, rect):
        self._cursor.paint(painter, QStyleOptionGraphicsItem())

    # Tries to insert the |block| in the list at index |line|.
    # Returns True is insertion was done, False otherwise.
    def _addBlockToLine(self, block, line):
        if len(self._lines) <= line:
            self._lines.append([] * (line - len(self._lines)))
            self._lines[line].append(block)
            self._onLineCountChange()
            return True

        for i in range(len(self._lines[line])):
            item = self._lines[line][i]
            # Block on the rigt, insert left.
            if item.x() >= block.x() + block.width():
                self._lines[line].insert(i, block)
                return True
            # Block on the left, continue checking.
            if item.x() + item.width() <= block.x():
                continue
            # Block neither on the right nor on the left, overlapping.
            return False

        # Not inserted yet, meaning block is at the end of the list.
        self._lines[line].append(block)
        return True

    # Add a block to the timeline.
    def addBlock(self, block):
        self.addItem(block)
        for i in range(len(self._lines) + 1):
            if self._addBlockToLine(block, i):
                block.setLine(i)
                break
        self._redrawScene()

    def reset(self : Self) -> None:
        for line in self._lines:
            for block in line:
                assert self.removeBlock(block)
        self._lines.clear()
        self._onLineCountChange()
        self._redrawScene()

    def removeBlock(self : Self, block : TimelineBlock) -> bool:
        for line in self._lines:
            if block in line:
                line.remove(block)
                self.removeItem(block)
                self._trimEmptyLines()
                self._redrawScene()
                return True
        return False

    def blockAt(self : Self, x : float, y : float) -> Optional[TimelineBlock]:
        line = self._pixelToLine(y)
        if len(self._lines) <= line:
            return None
        for block in self._lines[line]:
            if block.intersects(x, y):
                return block
        return None

    def cursorPosition(self : Self) -> int:
        return self._cursor.rawX()

    def updateCursorPosition(self, position):
        self._cursor.setRawX(position)
        self._redrawScene()

    def updateMediaDuration(self, duration):
        self._media_duration = duration
        self._background.setMediaDuration(duration)

    def _handleLeftClick(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        if self._cursor.intersects(event.scenePos().x(), event.scenePos().y()):
            self._dragState = DragState(event.scenePos(), self._cursor)
            return

        block = self.blockAt(event.scenePos().x(), event.scenePos().y())
        self._dragState = DragState(event.scenePos(), block)
        event.accept()

    def _handleRightClick(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        block = self.blockAt(event.scenePos().x(), event.scenePos().y())
        widget = self.views()[0]
        popupMenu = QMenu(I18N("edit"), widget)

        if block is not None:
            delete_action = QAction(I18N("delete"), widget)
            delete_action.triggered.connect(lambda: self.removeBlock(block))
            popupMenu.addAction(delete_action)

            edit_action = QAction(I18N("edit"), widget)
            edit_action.triggered.connect(lambda: self.on_symptom_edit.emit(block.symptom()))
            popupMenu.addAction(edit_action)

        popupMenu.popup(event.screenPos())
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._handleLeftClick(event)
        elif event.button() == Qt.RightButton:
            self._handleRightClick(event)

        #self.popupMenu.addAction(parent.actOpen)
        #self.popupMenu.addAction(parent.actSave)
        #self.popupMenu.addSeparator()
        #self.popupMenu.addAction(parent.actExit)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragState = None
        event.accept()

    def mouseMoveEvent(self, event):
        if self._dragState is None:
            return

        event.accept()
        if self._dragState.item() is None:
            self._handlePan(event)
            return

        if type(self._dragState.item()) == TimelineCursor:
            self._handleSeek(event)
            return

        if self._dragState.grabbedLeftHandle():
            self._handleLeftResize(event, self._dragState.item())
        elif self._dragState.grabbedRightHandle():
            self._handleRightResize(event, self._dragState.item())
        else:
            self._handleMove(event, self._dragState.item())

    def _handlePan(self, event):
        delta = self._dragState.latchDelta(event.scenePos())
        offset = max(0, self._offset - delta.x())
        self.setOffset(offset)

    def _getCollidingBlocks(self, line, x, width):
        if len(self._lines) <= line:
            return []

        colliders = []
        for item in self._lines[line]:
            if item.x() + item.width() <= x:
                continue

            # Early exit: list is sorted, we know no block will collide.
            if item.x() >= x + width:
                break
            colliders.append(item)
        return colliders

    def _trimEmptyLines(self : Self):
        line_trimmed = False
        for i in range(len(self._lines) - 1, -1, -1):
            if len(self._lines[i]) != 0:
                break
            self._lines.pop()
            line_trimmed = True
        if line_trimmed:
            self._onLineCountChange()

    def _moveBlock(self, block, new_line, new_x, new_width):
        self._lines[block.line()].remove(block)

        block.setX(new_x)
        block.setWidth(new_width)
        block.setLine(new_line)

        success = self._addBlockToLine(block, new_line)
        assert success
        self._trimEmptyLines()
        self._redrawScene()


    def _printLine(self, line):
        print("line {:2}: ".format(line), end="")
        for block in self._lines[line]:
            print("[ {:4} {:4} ]".format(block.x(), block.x() + block.width()), end="")
        print(" ")

    def _printLines(self, text):
        print("{}".format(text))
        for i in range(len(self._lines)):
            self._printLine(i)

    def _tryCommitBlockChange(self, block, new_line, new_x, new_width):
        colliders = self._getCollidingBlocks(new_line, new_x, new_width)
        colliders = [ x for x in colliders if x != block ]
        if len(colliders) == 0:
            self._moveBlock(block, new_line, new_x, new_width)
            return True
        return False

    def _handleMove(self, event, block):
        delta = self._dragState.delta(event.scenePos())

        new_x = max(0, self._dragState.item().x() + delta.x())
        new_line = self._pixelToLine(event.scenePos().y())

        if self._tryCommitBlockChange(block, new_line, new_x, block.width()):
            self._dragState.latchDelta(event.scenePos())

    def _handleLeftResize(self, event, block):
        delta = self._dragState.delta(event.scenePos())
        new_x = block.x() + delta.x()
        new_width = block.width() - delta.x()
        if new_width < TimelineBlock.HANDLE_CUTOFF:
            return
        if self._tryCommitBlockChange(block, block.line(), new_x, new_width):
            self._dragState.latchDelta(event.scenePos())

    def _handleRightResize(self, event, block):
        delta = self._dragState.delta(event.scenePos())
        new_x = block.x()
        new_width = block.width() + delta.x()
        if new_width < TimelineBlock.HANDLE_CUTOFF:
            return
        if self._tryCommitBlockChange(block, block.line(), new_x, new_width):
            self._dragState.latchDelta(event.scenePos())

    def _handleSeek(self, event):
        delta = self._dragState.latchDelta(event.scenePos())
        new_x = self._dragState.item().x() + delta.x()

        new_x = max(0, new_x)
        if self._media_duration is not None:
            new_x = min(new_x, self._media_duration * self._unit - self._offset)

        self._cursor.setX(new_x)
        self._redrawScene()
        self.on_seek.emit(self._cursor.rawX())

    def wheelEvent(self : Self, event : QWheelEvent, mouse_position : QPointF) -> None:
        # Normalized cursor position
        normalize = mouse_position.x() / self.sceneRect().width()

        old_start = self.offset()
        old_end = old_start + self.sceneRect().width() / self._unit
        # Coordinates (timeline local) of the aimed point.
        old_aimed = old_start + (old_end - old_start) * normalize

        # Apply zoom transformation
        if event.angleDelta().y() > 0:
            self._unit *= 1.25
        else:
            self._unit *= 1. / 1.25
        self.setUnit(self._unit)

        # Recompute start, end, aimed after the zoom.
        new_start = self.offset()
        new_end = new_start + self.sceneRect().width() / self._unit
        new_aimed = new_start + (new_end - new_start) * normalize

        # We want to point under the mouse to remains the same.
        delta = old_aimed - new_aimed
        required_shift = delta * self._unit
        if event.angleDelta().y() < 0:
            required_shift -= 1

        requested_offset = self.offset() + required_shift

        # Except we limit the left offset with the minumum value.
        requested_offset = max(0, requested_offset)
        self.setOffset(requested_offset)


class TimelineView(QGraphicsView):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        self.setMouseTracking(True)
        self._mouse_position = QPoint(0, 0)

        # Never show the horizontal scrollbar.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
        # Always show vertical ones.
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn);

    def wheelEvent(self, event):
        self.scene().wheelEvent(event, self._mouse_position)
        event.accept()

    def mouseMoveEvent(self, event):
        # QGraphicsView will forward this to the Scene, with conversions.
        super().mouseMoveEvent(event)
        self._mouse_position = event.position()

    def resizeEvent(self, event):
        self.scene().onWindowResize(event.size().width(), event.size().height())

class TimelineWidget(QWidget):
    on_seek = Signal(int)
    on_symptom_edit = Signal(Symptom)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._scene = TimelineScene()

        timeline = TimelineView(self._scene)
        layout = QVBoxLayout()
        layout.addWidget(timeline)
        self.setLayout(layout)
        self._scene.on_seek.connect(lambda x: self.on_seek.emit(x))
        self._scene.on_symptom_edit.connect(lambda x: self.on_symptom_edit.emit(x))

    def updateCursorPosition(self, position):
        self._scene.updateCursorPosition(position)

    def updateMediaDuration(self, duration):
        self._scene.updateMediaDuration(duration)

    def cursorTime(self : Self) -> int:
        return self._scene.cursorPosition()

    def addSymptomAtTime(self : Self, time : int, symptom : Symptom):
        assert symptom.isInstance()
        duration = self._scene.defaultBlockDuration()
        self._scene.addBlock(TimelineBlock(symptom, time, duration))

    def setTimeline(self : Self, timeline : Timeline):
        self._scene.reset()
        for item in timeline.getSymptoms():
            self._scene.addBlock(TimelineBlock(item.symptom, item.start, item.duration))

    def getTimeline(self : Self) -> Timeline:
        return self._scene.getTimeline()
