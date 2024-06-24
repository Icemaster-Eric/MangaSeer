import asyncio
from os import listdir
from PIL import Image, ImageFont, ImageDraw
import ujson
import aiohttp # try out aiohttp for web server?
from bs4 import BeautifulSoup


def get_conv_dataset():
    conv_dataset = []

    for file_name in listdir("datasets/dialogue/conv-json"):
        with open(f"datasets/dialogue/conv-json/{file_name}", "r", encoding="utf-8") as f:
            for dialogue in ujson.load(f):
                for utterance in dialogue["utterances"]:
                    conv_dataset.append(utterance["utterance"])

    return conv_dataset


async def get_kanji_in_page(session, level, page):
    async with session.get(
        f"https://kanjikana.com/en/kanji/kanken/{level}/pages/{page}"
    ) as response:
        html = await response.text()
        soup = BeautifulSoup(html, features="html.parser")
        kanji_list = [
            elem.find("h3") for elem in soup.find_all("a", class_="linkbox square")
        ]

    return [kanji.get_text() for kanji in kanji_list]


async def get_kanken_kanji(session, level):
    tasks = []

    for page in await get_pages(session, level):
        tasks.append(get_kanji_in_page(session, level, page))

    results = await asyncio.gather(*tasks)

    return [j for i in results for j in i]


async def get_pages(session, level) -> range:
    async with session.get(
        f"https://kanjikana.com/en/kanji/kanken/{level}"
    ) as response:
        html = await response.text()
        soup = BeautifulSoup(html, features="html.parser")
        pages = soup.find("a", class_="Pagination_active__3ntIl").get_text()

    return range(int(pages[0]), int(pages.split(" / ")[-1]))


async def get_kanji():
    tasks = []

    async with aiohttp.ClientSession() as session:
        for level in (10, 9, 8, 7, 6, 5, 4, 3, 2.5, 2, 1.5, 1):
            tasks.append(get_kanken_kanji(session, level))

        kanji_list = await asyncio.gather(*tasks)

    return [kanji for sub in kanji_list for kanji in sub]


async def main():
    #conv_dataset = get_conv_dataset()

    kanji_list = await get_kanji()

    with open("kanji.txt", "a", encoding="utf-8") as f:
        for kanji in kanji_list:
            f.write(f"{kanji}\n")


if __name__ == "__main__":
    asyncio.run(main())