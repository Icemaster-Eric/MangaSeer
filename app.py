from PySide6 import QtWidgets, QtCore


class Popup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("kawaii little popup")
        label.move(50, 50)

        layout.addWidget(label)

        self.setLayout(layout)


class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 100, 100)

        layout = QtWidgets.QVBoxLayout()

        # NOTE: choose a better name than "popup"
        self.popups = [
            Popup()
        ]
        for popup in self.popups:
            layout.addWidget(popup)

        self.setLayout(layout)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setCentralWidget(Overlay())
        self.showMaximized()


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    window = MainWindow()
    app.exec()
