from html2image import Html2Image


hti = Html2Image("edge", size=(500, 500), custom_flags=["--no-sandbox"])

css_str = """
@font-face {
    font-family: "GenEiPOP";
    src: url("E:/Code/MangaSeer/datasets/fonts/GenEiPOPlePw-Bk.ttf");
}
body {
    background-color: black;
}
p {
    font-family: "GenEiPOP";
    font-size: 48px;
    color: black;
    -webkit-text-stroke: 2px white;
    writing-mode: vertical-rl;
    text-orientation: upright;
}
"""

hti.screenshot(
    html_str="<body><p><ruby>今<rt>いま</rt></ruby>まで<ruby>一人<rt>ひとり</rt></ruby>で<ruby>来<rt>く</rt></ruby>るたことは<ruby>有<rt>あ</rt></ruby>るますずが、<ruby>私<rt>わたし</rt></ruby>の<ruby>家<rt>いえ</rt></ruby>までの<ruby>交通<rt>こうつう</rt></ruby><ruby>手段<rt>しゅだん</rt></ruby>は<ruby>分<rt>わ</rt></ruby>かるますか?</p></body>",
    css_str=css_str, save_as="ss.png"
)


class Renderer:
    def __init__(self):
        self.hti = Html2Image("edge", size=(500, 500), custom_flags=["--no-sandbox"])

    def render(html):
        # calculate bounding box of rendered html and crop it using Pillow as postprocessing step (`getbbox` function)
        pass
