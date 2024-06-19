from PySide6 import QtWidgets, QtCore


class Popup(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout()

        layout.addWidget(QtWidgets.QLabel("ayaya"))

        self.setLayout(layout)

        self.setStyleSheet("QWidget { background-color : green}") # debugging
        self.setGeometry(100, 100, self.sizeHint().width(), self.sizeHint().height())
        self.setFixedSize(100, 100)

        self.show()


class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # NOTE: choose a better name than "popup"
        self.popups = [
            Popup(self)
        ]

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.showMaximized()


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    overlay = Overlay()
    app.exec()
