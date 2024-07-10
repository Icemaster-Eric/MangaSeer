from PySide6 import QtWidgets, QtCore, QtGui
from ultralytics import YOLOv10
from manga_ocr import MangaOcr
from utils import screenshot, tts, JMDict, KeyboardListener


class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QtWidgets.QSizePolicy.ControlType.PushButton, QtWidgets.QSizePolicy.ControlType.PushButton, QtCore.Qt.Orientation.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


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


class WordInfo(QtWidgets.QWidget):
    def __init__(self, word: dict):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        if "reading" in word:
            reading_label = QtWidgets.QLabel(f"Reading: {word['reading']}")
            reading_label.setStyleSheet("QLabel { font-family: 'Noto Sans JP'; font-size: 15px; }")
            layout.addWidget(reading_label)

        for i, sense in enumerate(word["senses"]):
            if i != 0:
                layout.addSpacerItem(QtWidgets.QSpacerItem(100, 10))

            # really ugly code below but whatever, might clean this up in the future
            if sense["pos"]:
                pos_label = QtWidgets.QLabel(f"Part of Speech: {', '.join(sense['pos'])}")
                pos_label.setStyleSheet("QLabel { font-family: 'Noto Sans JP'; font-size: 15px; }")
                layout.addWidget(pos_label)

            if sense["gloss"]:
                for gloss in sense["gloss"]:
                    gloss_label = QtWidgets.QLabel(
                        f"Glossary: {gloss['text']}" + (f" ({gloss['gender']})" if gloss["gender"] else "") + f" ({gloss['lang']})"
                    )
                    gloss_label.setStyleSheet("QLabel { font-family: 'Noto Sans JP'; font-size: 15px; }")
                    layout.addWidget(gloss_label)
                    #if gloss["gender"]:
                    #    gender_label = QtWidgets.QLabel(f"Gender: {gloss['gender']}")

            if sense["info"]:
                info_label = QtWidgets.QLabel(f"Info: {sense['info']}")
                info_label.setStyleSheet("QLabel { font-family: 'Noto Sans JP'; font-size: 15px; }")
                layout.addWidget(info_label)

            if sense["field"]:
                field_label = QtWidgets.QLabel(f": {', '.join(sense['field'])}")
                field_label.setStyleSheet("QLabel { font-family: 'Noto Sans JP'; font-size: 15px; }")
                layout.addWidget(field_label)

            if sense["dialect"]:
                dialect_label = QtWidgets.QLabel(f"Dialect: {', '.join(sense['dialect'])}")
                dialect_label.setStyleSheet("QLabel { font-family: 'Noto Sans JP'; font-size: 15px; }")
                layout.addWidget(dialect_label)

            if sense["misc"]:
                misc_label = QtWidgets.QLabel(f"Miscellaneous: {', '.join(sense['misc'])}")
                misc_label.setStyleSheet("QLabel { font-family: 'Noto Sans JP'; font-size: 15px; }")
                layout.addWidget(misc_label)


class DictWord(QtWidgets.QLabel):
    def __init__(self, word: dict, info_widget: QtWidgets.QListWidget):
        super().__init__(word["text"])

        self.word = word
        self.info_widget = info_widget

        self.setStyleSheet("QLabel { font-family: 'Noto Sans JP'; font-size: 20px; border-radius: 5px; } QLabel:hover { background-color: rgba(0, 191, 255, 0.5); }")
        self.setCursor(QtGui.Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        self.info_widget.clear()

        if self.word["type"] == "word":
            for word in self.word["words"]:
                word_item = QtWidgets.QListWidgetItem(self.info_widget)
                word_info = WordInfo(word)
                word_item.setSizeHint(word_info.sizeHint())

                self.info_widget.addItem(word_item)
                self.info_widget.setItemWidget(word_item, word_info)


class Dictionary(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget, text: str):
        super().__init__(parent)

        words = jmdict.lookup(text, common=True)

        self.setWindowTitle("Dictionary")
        self.setFixedWidth(600)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        info_widget = QtWidgets.QListWidget()
        info_widget.setVerticalScrollMode(QtWidgets.QListWidget.ScrollMode.ScrollPerPixel)

        text_widget = QtWidgets.QWidget()
        text_layout = FlowLayout()
        text_widget.setLayout(text_layout)
        text_layout.setSpacing(0)

        for word in words:
            if not word["type"]:
                text_label = QtWidgets.QLabel(word["text"])
                text_label.setStyleSheet("QLabel { font-family: 'Noto Sans JP'; font-size: 20px; }")
            else:
                text_label = DictWord(word, info_widget)

            text_layout.addWidget(text_label)

        layout.addWidget(text_widget)
        layout.addWidget(info_widget)


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

        self.yolo_model = YOLOv10("models/yolo/yolov10l.pt")
        self.ocr_model = MangaOcr()
        self.popups: list[Popup] = []
        self.bbox = bbox
        self.previous_ss = None

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.setGeometry(
            bbox[0],
            bbox[1],
            bbox[2] - bbox[0],
            bbox[3] - bbox[1]
        )
        self.show()

    def scan_screen(self):
        # rename this function & make it run in separate thread
        # change to more universal ss method later
        ss = screenshot(self.bbox)

        self.previous_ss = ss

        bboxes = self.yolo_model(
            source=ss,
            conf=0.3,
            classes=[0, 1],
            agnostic_nms=True,
            verbose=False
        )[0].boxes

        for popup in self.popups:
            popup.hide()
            popup.deleteLater()

        self.popups.clear()

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

        self.overlay = None

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
    
    def on_shortcut_triggered(self):
        if self.overlay:
            self.overlay.scan_screen()


if __name__ == "__main__":
    jmdict = JMDict("jmdict.db", "jmnedict.db")

    app = QtWidgets.QApplication()

    QtGui.QFontDatabase.addApplicationFont("fonts/NotoSansJP.ttf")
    font = QtGui.QFont("Noto Sans JP")

    window = MainWindow()
    """overlay = Overlay((200, 200, 400, 400))
    test_popup = Popup(
        (0, 0, 50, 70),
        "酔い止め薬を一度だけ試しましたが、効果は感じられませんでした。",
        overlay
    )"""

    listener = KeyboardListener()
    listener.trigger_function.connect()

    app.exec()
