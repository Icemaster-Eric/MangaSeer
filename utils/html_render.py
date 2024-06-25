from PySide6 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets


class Render(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, html_to_render: set[str]):
        super().__init__()

        self.current_html = None
        self.html_to_render = html_to_render

        #self.loadFinished.connect(self._loadFinished)

        self.setHtml(self.html_to_render.pop())
        self.printFinished.connect(self._loadFinished)

        while len(self.html_to_render):
            while not self.current_html:
                app.processEvents(QtCore.QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents | QtCore.QEventLoop.ProcessEventsFlag.ExcludeSocketNotifiers | QtCore.QEventLoop.ProcessEventsFlag.WaitForMoreEvents)

            self.screenshot()
            print("ss!!!")
            self.current_html = None

        app.quit()

    def _loadFinished(self, data):
        self.current_html = data

    def screenshot(self):
        self.grab().save(f"ss.png", "png")


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    render = Render([f"<h1>{i} some text here idk {i}" for i in range(50)])
    app.exec()
