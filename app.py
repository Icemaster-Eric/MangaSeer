from PySide6 import QtWidgets, QtCore, QtGui
#from ultralytics import YOLOv10
#from manga_ocr import MangaOcr
from utils import screenshot, tts, JMDict


class TextEdit(QtWidgets.QInputDialog):
    def __init__(self, parent: QtWidgets.QWidget, text: str):
        super().__init__(parent)

        self.setWindowTitle("Edit Text")
        self.setInputMode(QtWidgets.QInputDialog.InputMode.TextInput)
        self.setLabelText("Enter text:")
        line_edit = self.findChild(QtWidgets.QLineEdit)
        line_edit.setFont("Noto Sans JP")
        line_edit.setText(text)


class PopupButton(QtWidgets.QPushButton):
    def __init__(self, icon: str):
        super().__init__(QtGui.QIcon(icon), "")
        self.setStyleSheet("QPushButton { background-color: rgb(60, 60, 60); } QPushButton:hover { background-color: rgb(52, 52, 52); } QPushButton::pressed { background-color: rgb(35, 35, 35); }")
        self.setCursor(QtGui.Qt.CursorShape.PointingHandCursor)


class DictWord(QtWidgets.QLabel):
    def __init__(self, text: str, layout: QtWidgets.QVBoxLayout):
        super().__init__(text)

        self.t = text
        self.l = layout

        self.setStyleSheet("QLabel { font-size: 24px; } QLabel:hover { background-color: powderblue; }")
        self.setFont("Noto Sans JP")
    
    def mousePressEvent(self, event):
        self.l.addWidget(
            QtWidgets.QLabel(self.t)
        )


class Dictionary(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget, text: str):
        super().__init__(parent)

        words = jmdict.lookup(text, common=True)

        self.setWindowTitle("Dictionary")

        layout = QtWidgets.QVBoxLayout()

        text_widget = QtWidgets.QWidget()
        text_layout = QtWidgets.QHBoxLayout()
        text_layout.setSpacing(0)

        for word in words:
            text_label = DictWord(word["text"], layout)
            text_layout.addWidget(text_label)

        text_widget.setLayout(text_layout)

        layout.addWidget(text_widget)

        self.setLayout(layout)


class Popup(QtWidgets.QWidget):
    def __init__(self, bbox: list[int, int, int, int], text: str, parent: QtWidgets.QWidget):
        super().__init__(parent)

        self.text = text
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.text_outline = QtWidgets.QLabel()
        self.text_outline.setStyleSheet("QWidget { background-color: rgba(0,0,0,0.01); }")
        self.text_outline.setFixedSize(bbox[2] - bbox[0], bbox[3] - bbox[1])

        layout.addWidget(self.text_outline)

        self.button_container = QtWidgets.QWidget()
        self.button_container.setStyleSheet("QWidget { background-color: rgba(0,0,0,0.01); }")
        self.button_container.setFixedHeight(0)
        button_layout = QtWidgets.QGridLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        edit_button = PopupButton("icons/edit.svg")
        tts_button = PopupButton("icons/tts.svg")
        dictionary_button = PopupButton("icons/dictionary.svg")
        save_button = PopupButton("icons/save.svg")

        edit_button.clicked.connect(self.edit_text)
        tts_button.clicked.connect(self.tts)
        dictionary_button.clicked.connect(self.dictionary)

        button_layout.addWidget(edit_button, 0, 0)
        button_layout.addWidget(save_button, 0, 1)
        button_layout.addWidget(tts_button, 1, 0)
        button_layout.addWidget(dictionary_button, 1, 1)

        self.button_container.setLayout(button_layout)
        layout.addWidget(self.button_container)

        self.setLayout(layout)

        self.move(*bbox[:2])
        self.show()

    def enterEvent(self, event):
        self.text_outline.setStyleSheet("QWidget { background-color: rgba(0,0,0,0.01); border: 2px solid royalblue; }")
        self.button_container.setFixedHeight(self.button_container.minimumSizeHint().height())

    def leaveEvent(self, event):
        self.text_outline.setStyleSheet("QWidget { background-color: rgba(0,0,0,0.01); }")
        self.button_container.setFixedHeight(0)

    def edit_text(self):
        dialog = TextEdit(self, self.text)

        if dialog.exec() and dialog.textValue():
            self.text = dialog.textValue()

    def tts(self):
        tts(self.text)
    
    def dictionary(self):
        dictionary = Dictionary(self, self.text)

        dictionary.exec()


class Overlay(QtWidgets.QWidget):
    def __init__(self, bbox):
        super().__init__()

        #self.yolo_model = YOLOv10("models/yolo/yolov10l.pt")
        #self.ocr_model = MangaOcr()
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

        select_region = QtWidgets.QWidget()
        select_region.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.2); }")
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
    jmdict = JMDict("jmdict.db", "jmnedict.db")

    app = QtWidgets.QApplication()

    QtGui.QFontDatabase.addApplicationFont("fonts/NotoSansJP.ttf")
    font = QtGui.QFont("Noto Sans JP")

    #window = MainWindow()
    overlay = Overlay((200, 200, 400, 400))
    test_popup = Popup(
        (0, 0, 50, 70),
        "はい。酔い止め薬を一度だけ試しましたが、効果は感じられませんでした。",
        overlay
    )
    app.exec()
