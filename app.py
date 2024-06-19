from PySide6 import QtWidgets, QtCore


class Popup(QtWidgets.QWidget):
    def __init__(self, bbox: tuple[int, int, int, int], parent: QtWidgets.QWidget):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout()

        layout.addWidget(QtWidgets.QLabel("ayaya"))

        self.setLayout(layout)

        self.setStyleSheet("QWidget { border : 3px solid red}")
        #self.setGeometry(0, 0, self.sizeHint().width(), self.sizeHint().height())
        self.setGeometry(*bbox)
        self.show()

    def mousePressEvent(self, event):
        print(type(event))


class Overlay(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        # NOTE: choose a better name than "popup"
        self.popups = [
            Popup((100, 100, 200, 200), self)
        ]

        self.move(0, 0)
        self.showMaximized()


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    overlay = Overlay()
    app.exec()
