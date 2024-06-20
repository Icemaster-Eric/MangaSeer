from PySide6 import QtWidgets, QtCore, QtGui
from ultralytics import YOLOv10
from PIL import Image
import dxcam
import time


class Popup(QtWidgets.QWidget):
    def __init__(self, bbox: list[int, int, int, int], parent: QtWidgets.QWidget):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout()

        layout.addWidget(QtWidgets.QLabel("ayaya"))

        self.setLayout(layout)

        self.setStyleSheet("QWidget { border: 3px solid red }")
        #self.setGeometry(0, 0, self.sizeHint().width(), self.sizeHint().height())
        self.setGeometry(
            bbox[0] - bbox[2] / 2,
            bbox[1] - bbox[3] / 2,
            bbox[2],
            bbox[3]
        )
        self.show()

    def mousePressEvent(self, event):
        print(type(event))


class Overlay(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = YOLOv10("models/2.pt")
        self.camera = dxcam.create()
        self.popups: list[Popup] = []

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.move(0, 0)
        self.showMaximized()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.scan_screen)
        self.timer.start()

    def scan_screen(self):
        # rename this function
        for popup in self.popups:
            popup.hide()

        app.processEvents()

        start = time.time()
        snapshot = Image.fromarray(self.camera.grab())
        print(time.time() - start)

        for popup in self.popups:
            popup.show()
            popup.deleteLater()

        self.popups.clear()
        app.processEvents()

        bboxes = self.model(source=snapshot, conf=0.25)[0].boxes

        for bbox in bboxes:
            self.popups.append(Popup(
                bbox.xywh.tolist()[0],
                self
            ))

        self.showMaximized()


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    overlay = Overlay()
    app.exec()
