import pytest
from PySide6.QtCore import Qt, Signal
from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api
from PySide6.QtWidgets import QWidget, QPushButton, QTabWidget, QToolButton, QStackedWidget

from episcope.gui import ClickableVideoWidget

@pytest.mark.filterwarnings('ignore::RuntimeWarning') # Pytest internal binding issue.
def test_click_signal(qtbot):
    widget = ClickableVideoWidget()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)

    with qtbot.waitSignal(widget.clicked) as blocker:
        qtbot.mouseClick(widget, Qt.MouseButton.LeftButton)
