from PyQt6.QtWidgets import QApplication
import sys

from episcope.gui.player import Player

# App as a global is a workaround for an issue with QT threading.
# QT has some background treads running, and if this gets deleted
# before the main window, there is a SIGSEGV.
app = None

def main():
    global app
    app = QApplication(sys.argv)
    main_win = Player()
    available_geometry = main_win.screen().availableGeometry()
    main_win.resize(available_geometry.width() / 3,
                    available_geometry.height() / 2)
    main_win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
