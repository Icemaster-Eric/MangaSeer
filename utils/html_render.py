from html2image import Html2Image


hti = Html2Image("edge", size=(500, 500), custom_flags=["--no-sandbox"])

css_str = """
@font-face {
    font-family: "GenEiPOP";
    src: url("E:/Code/MangaSeer/datasets/fonts/GenEiPOPlePw-Bk.ttf");
}
body {
    background-color: white;
    font-size: 32px;
}
p {
    font-family: "GenEiPOP";
    writing-mode: vertical-rl;
    text-orientation: upright;
}
"""

hti.screenshot(html_str="<p><ruby>具合<rt>ぐあい</rt></ruby>は、どうで<ruby>具合<rt>ぐあい</rt></ruby>すか?</p>", css_str=css_str, save_as="ss.png")


class Renderer:
    def __init__(self):
        self.hti = Html2Image("edge", size=(500, 500), custom_flags=["--no-sandbox"])

    def render(html):
        # calculate bounding box of rendered html and crop it using Pillow as postprocessing step (`getbbox` function)
        pass
