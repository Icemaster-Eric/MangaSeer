from os import listdir
import random
from PIL import Image, ImageFont, ImageDraw
import ujson
from tqdm import tqdm


def get_conv_dataset():
    conv_dataset = []

    for file_name in listdir("datasets/japanese/conv-json"):
        with open(f"datasets/japanese/conv-json/{file_name}", "r", encoding="utf-8") as f:
            for dialogue in ujson.load(f):
                for utterance in dialogue["utterances"]:
                    conv_dataset.append(utterance["utterance"])

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


def generate_synthetic_dataset(kanji: tuple) -> set:
    hiragana = "".join(chr(i) for i in range(int("3040", 16), int("309F", 16)))
    katakana = "".join(chr(i) for i in range(int("30A0", 16), int("31FF", 16)))
    choices = (
        1,
        1,
        1,
        *hiragana,
        *katakana,
        *kanji
    )
    weights = (
        "...",
        "....",
        ".....",
        *[20 for _ in range(len(hiragana))],
        *[5 for _ in range(len(katakana))],
        *[50 for _ in range(len(kanji))]
    )
    return set(tqdm(
        ("".join(random.choices(choices, weights) for _ in range(1, 30)) for _ in range(40000)),
        total=40000
    ))


def main():
    conv_dataset = get_conv_dataset()
    kanji_set = tuple(get_kanji())
    synth_dataset = generate_synthetic_dataset(kanji_set)
    print(synth_dataset[:5], sep="\n")


if __name__ == "__main__":
    main()
