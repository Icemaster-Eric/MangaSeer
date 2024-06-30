from PySide6 import QtWidgets, QtCore, QtGui
#from ultralytics import YOLOv10
#from manga_ocr import MangaOcr
from utils import screenshot


class Popup(QtWidgets.QWidget):
    def __init__(self, bbox: list[int, int, int, int], text: str, parent: QtWidgets.QWidget):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        text_outline = QtWidgets.QLabel()
        text_outline.setStyleSheet("QWidget { border: 2px solid royalblue; }")
        text_outline.setFixedSize(bbox[2] - bbox[0], bbox[3] - bbox[1])
        layout.addWidget(text_outline)

        button_container = QtWidgets.QWidget()
        button_layout = QtWidgets.QGridLayout()

        tts_button = QtWidgets.QPushButton(QtGui.QIcon("icons/tts.svg"), "")
        button_layout.addWidget(tts_button, 0, 0)

        furigana_button = QtWidgets.QPushButton(QtGui.QIcon("icons/furigana.svg"), "")
        button_layout.addWidget(furigana_button, 1, 0)

        dictionary_button = QtWidgets.QPushButton(QtGui.QIcon("icons/dictionary.svg"), "")
        button_layout.addWidget(dictionary_button, 0, 1)

        translate_button = QtWidgets.QPushButton(QtGui.QIcon("icons/translate.svg"), "")
        button_layout.addWidget(translate_button, 1, 1)

        button_container.setLayout(button_layout)
        layout.addWidget(button_container)

        #QtGui.QIcon("icons/")
        #layout.addWidget(QtWidgets.QLabel(text))
        #self.setStyleSheet("QWidget { color: red; width: 100px; }")

        self.setLayout(layout)

        self.move(*bbox[:2])
        self.show()

class Overlay(QtWidgets.QWidget):
    def __init__(self, bbox):
        super().__init__()

        #self.yolo_model = YOLOv10("models/yolo/yolov10l.pt")
        #self.ocr_model = MangaOcr()
        self.popups: list[Popup] = []
        self.bbox = bbox

        #self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.setGeometry(
            bbox[0],
            bbox[1],
            bbox[2] - bbox[0],
            bbox[3] - bbox[1]
        )
        self.show()

        """self.timer = QtCore.QTimer()
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.scan_screen)
        self.timer.start()"""

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

        for bbox in bboxes:
            x, y, w, h = bbox.xywh.tolist()[0]
            w += 8
            h += 8
            x1 = x - w / 2
            y1 = y - h / 2
            x2, y2 = x1 + w, y1 + h
            bbox_image = ss.crop((x1, y1, x2, y2))
            text = self.ocr_model(bbox_image)
            self.popups.append(Popup(
                (x1, y1, x2, y2),
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
        #layout.setContentsMargins(0, 0, 0, 0)

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
    #window = MainWindow()
    overlay = Overlay((200, 200, 400, 400))
    test_popup = Popup((0, 0, 50, 100), "hello world", overlay)
    app.exec()
