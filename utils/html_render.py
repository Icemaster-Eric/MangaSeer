from uuid import uuid4
from random import choice, randint
from os import remove, listdir
from html2image import Html2Image
from PIL import Image, ImageOps


class Renderer:
    def __init__(self):
        self.hti = Html2Image("edge", size=(640, 640), custom_flags=["--no-sandbox"], output_path="rendered_images")
        self.css_str = (
            "@font-face"
            "{font-family:'customFont';src:url('%s');}"
            "body"
            "{ background:black;}"
            "p"
            "{font-family:'customFont';"
            "font-size:%spx;"
            "font-weight:%s;"
            "color:%s;"
            "-webkit-text-stroke:%s;"
            "border:1px solid red;"
            "writing-mode:%s;" # vertical-rl
            "text-orientation:upright;"
            "background:%s;"
            "padding:%s;"
            "width:%s;"
            "height:%s;}"
        )
        self.fonts = [f"E:/Code/MangaSeer/datasets/fonts/{font}" for font in listdir("datasets/fonts")]
        self.styles = (
            ("black", "0", "white"),
            ("white", "2px black", "white")
        )

    def render(self, html: str, options: tuple[str, str, str, str, str, str, str]) -> None:
        ssid = uuid4().hex
        self.hti.screenshot(html_str=html, css_str=self.css_str % options, save_as=f"{ssid}.png")

        image = Image.open(f"rendered_images/{ssid}.png")
        bbox = image.getbbox()
        bbox = (bbox[0] + 1, bbox[1] + 1, bbox[2] - 1, bbox[3] - 1)
        image.crop(bbox).save(f"rendered_images/{ssid}.jpg", format="jpeg")

        remove(f"rendered_images/{ssid}.png")

    def get_preset(self) -> tuple[str]:
        """Returns a random preset for a render

        Returns:
            tuple[str]: A valid preset for the `options` parameter of `Renderer.render`
        """
        font = choice(self.fonts)
        style = choice(self.styles)
        writing_mode = "vertical-rl"
        padding = f"{randint(1,7)}px {randint(1,7)}px {randint(1,7)}px {randint(1,7)}px"
        width = "auto"
        height = f"{randint(300, 600)}px"

        return font, *style, writing_mode, padding, width, height


if __name__ == "__main__":
    for file_name in listdir("rendered_images"):
        remove(f"rendered_images/{file_name}")

    renderer = Renderer()

    for _ in range(10):
        renderer.render(
            (
                "<p><ruby>其<rt>その</rt></ruby>れは<ruby>名案<rt>めいあん</rt></ruby>ですね。"
                "<ruby>口コミ<rt>くちこみ</rt></ruby>サイトで<ruby>調<rt>しら</rt></ruby>べるて"
                "<ruby>友達<rt>ともだち</rt></ruby>と<ruby>相談<rt>そうだん</rt></ruby>"
                "<ruby>為<rt>す</rt></ruby>るたいと<ruby>思<rt>おも</rt></ruby>うます。"
                "<ruby>比較<rt>ひかく</rt></ruby><ruby>的<rt>てき</rt></ruby>"
                "<ruby>手頃<rt>てごろ</rt></ruby>だ<ruby>価格<rt>かかく</rt></ruby>で、"
                "<ruby>料理<rt>りょうり</rt></ruby>が<ruby>美味し<rt>おいし</rt></ruby>い"
                "<ruby>御<rt>お</rt></ruby><ruby>店<rt>みせ</rt></ruby>が"
                "<ruby>見付か<rt>みつか</rt></ruby>ると<ruby>良<rt>よ</rt></ruby>いのですが。</p>"
            ),
            renderer.get_preset()
        )
