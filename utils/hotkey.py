from pynput import keyboard
from PySide6 import QtCore


class KeyboardListener(QtCore.QThread):
    trigger_function = QtCore.Signal()

    def __init__(self):
        super().__init__()

    def run(self):
        with keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+s": self.on_trigger
        }) as listener:
            listener.join()

    def on_trigger(self):
        self.trigger_function.emit()
