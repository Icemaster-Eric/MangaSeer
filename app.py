from PySide6 import QtWidgets, QtCore
from ultralytics import YOLOv10
from manga_ocr import MangaOcr
from utils import screenshot
from tqdm import tqdm # temporary for testing speed

class Popup(QtWidgets.QWidget):
    def __init__(self, bbox: list[int, int, int, int], text: str, parent: QtWidgets.QWidget):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout()

        layout.addWidget(QtWidgets.QLabel(text))

        self.setLayout(layout)

        self.setStyleSheet("QWidget { border: 2px solid lightblue; color: red; margin: 0px; padding: 0px }")
        #self.setGeometry(0, 0, self.sizeHint().width(), self.sizeHint().height())
        self.setGeometry(*bbox)
        self.show()

    def mousePressEvent(self, event):
        print(type(event))


class Overlay(QtWidgets.QWidget):
    def __init__(self, bbox):
        super().__init__()

        self.yolo_model = YOLOv10("models/yolo/yolov10l.pt")
        self.ocr_model = MangaOcr()
        self.popups: list[Popup] = []
        self.bbox = bbox

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.setGeometry(
            bbox[0],
            bbox[1],
            bbox[2] - bbox[0],
            bbox[3] - bbox[1]
        )
        self.show()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.scan_screen)
        self.timer.start()

    def scan_screen(self):
        # rename this function & make it run in separate thread
        for popup in self.popups:
            popup.hide()
            popup.deleteLater()

        self.popups.clear()

        # change to more universal ss method later
        ss = screenshot(self.bbox)

        bboxes = self.yolo_model(
            source=ss,
            conf=0.3,
            classes=[0, 1],
            agnostic_nms=True,
            verbose=False
        )[0].boxes

        for bbox in tqdm(bboxes):
            x, y, w, h = bbox.xywh.tolist()[0]
            w += 22
            h += 22
            x = x - w / 2
            y = y - h / 2
            bbox_image = ss.crop((x, y, x + w, y + h))
            text = self.ocr_model(bbox_image)
            self.popups.append(Popup(
                (x, y, w, h),
                text,
                self
            ))

        app.processEvents()


class MainWindow(QtWidgets.QWidget): # no need for actual main window widget (?)
    def __init__(self):
        super().__init__()

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

        layout = QtWidgets.QVBoxLayout()

        select_region = QtWidgets.QWidget()
        select_region.setStyleSheet("QWidget { background-color: rgba(0, 150, 255, 0.3); }")
        select_region.setFixedSize(self.maximumSize())
        select_region.mousePressEvent = self.select_region_start
        select_region.mouseReleaseEvent = self.select_region_end

        layout.addWidget(select_region)

        self.setLayout(layout)

        self.move(0, 0)
        self.showMaximized()

    def select_region_start(self, event):
        self.overlay_x = event.globalPosition().x()
        self.overlay_y = event.globalPosition().y()

    def select_region_end(self, event):
        self.overlay = Overlay((
            int(self.overlay_x), int(self.overlay_y),
            int(event.globalPosition().x()),
            int(event.globalPosition().y())
        ))
        self.hide()


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    window = MainWindow()
    app.exec()
