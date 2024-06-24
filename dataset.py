from os import listdir
import random
from PIL import Image, ImageFont, ImageDraw
import ujson
from tqdm import tqdm
import pykakasi


def get_conv_dataset() -> set:
    conv_dataset = set()

    for file_name in listdir("datasets/japanese/conv-json"):
        with open(f"datasets/japanese/conv-json/{file_name}", "r", encoding="utf-8") as f:
            for dialogue in ujson.load(f):
                for utterance in dialogue["utterances"]:
                    conv_dataset.add(utterance["utterance"])

    return conv_dataset


def get_kanji() -> set:
    with open("datasets/japanese/kanji.txt", "r", encoding="utf-8") as f:
        kanji_list = f.readlines()

    return set(kanji.strip() for kanji in kanji_list)


def preprocess_sentence(sentence: str):
    for i, c in enumerate(sentence.strip()):
        if c.isnumeric() or c.isspace():
            continue
        break

    return sentence[i:]


def extract_sentences(path) -> set:
    with open(path, "r", encoding="utf-8") as f:
        sentences = f.readlines()

    return set(tqdm(
        (preprocess_sentence(sentence) for sentence in sentences),
        total=100000
    ))


def get_news_dataset() -> set:
    with open("datasets/japanese/news_dataset.txt", "r", encoding="utf-8") as f:
        sentences = f.readlines()

    return set(sentence.strip() for sentence in sentences)


def main():
    conv_dataset = get_conv_dataset()
    #news_dataset = get_news_dataset()
    #dataset = conv_dataset.union(news_dataset)
    kanji_set = tuple(get_kanji())

    kks = pykakasi.kakasi()
    text = conv_dataset.pop()
    result = kks.convert(text)
    for item in result:
        print("{}[{}] ".format(item["orig"], item["kana"].capitalize()), end="")
    print()


if __name__ == "__main__":
    main()
