from uuid import uuid4
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
            "{ background:%s;}"
            "p"
            "{font-family:'customFont';"
            "font-size:%spx;"
            "color:%s;"
            "-webkit-text-stroke:%s;"
            "writing-mode:%s;" # vertical-rl
            "text-orientation:upright;}"
        )

    def render(self, html: str, options: tuple[str, str, str, str, str, str, str]) -> None:
        ssid = uuid4().hex
        self.hti.screenshot(html_str=html, css_str=self.css_str % options, save_as=f"{ssid}.png")

        image = Image.open(f"rendered_images/{ssid}.png")

        if options[1] == "white":
            bbox = image.getbbox()
        elif options[1] == "black" and options[1] == "white":
            bbox = ImageOps.invert(image).getbbox()
        else:
            pass

        image.crop(bbox).save(f"rendered_images/{ssid}.jpg", format="jpeg")

        remove(f"rendered_images/{ssid}.png")


if __name__ == "__main__":
    renderer = Renderer()
    presets = []
    fonts = [f"datasets/fonts/{font}" for font in listdir("datasets/fonts")]

    for font in fonts:
        for font_size in (12, 15, 18, 21):
            presets.append((font, "white", font_size, "black", "0", "vertical-rl"))
            presets.append((font, "black", font_size, "black", "1px white", "vertical-rl"))
            presets.append((font, "white", font_size, "black", "0", "vertical-rl"))
            presets.append((font, "black", font_size, "black", "1px white", "vertical-rl"))
        # white bg with black text
        # picture bg with white outlined black text
        # different font sizes
        # vertical/horizontal text

    for preset in presets:
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
            preset
        )
