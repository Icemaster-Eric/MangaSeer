from os import listdir
import random
from PIL import Image, ImageFont, ImageDraw
import ujson
from tqdm import tqdm
import re


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
    hiragana = [chr(i) for i in range(int("3041", 16), int("3097", 16))]
    katakana = [chr(i) for i in range(int("30A1", 16), int("30FF", 16))]
    hiragana = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわをんゔゕゖ"
    katakana = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヲンヴヵヶヺ"
    choices = (
        "...",
        ".....",
        "ー",
        *hiragana,
        *katakana,
        *kanji
    )
    weights = (
        50,
        50,
        50,
        *([1500] * len(hiragana)),
        *([500] * len(katakana)),
        *([30] * len(kanji))
    )
    return set(tqdm(
        ("".join(random.choices(choices, weights, k=random.randint(1, 30))) for _ in range(40000)),
        total=40000
    ))


def get_synth_dataset() -> set:
    with open("datasets/japanese/synth_dataset.txt", "r", encoding="utf-8") as f:
        dataset = f.readlines()

    return set(sentence.strip() for sentence in dataset)


def main():
    conv_dataset = get_conv_dataset()
    kanji_set = tuple(get_kanji())
    #synth_dataset = get_synth_dataset()


if __name__ == "__main__":
    #main()
    with open("datasets/japanese/news_dataset.txt", "r", encoding="utf-8") as f:
        dataset = f.readlines()

    with open("datasets/japanese/news_dataset_clean.txt", "a", encoding="utf-8") as f:
        for sentence in tqdm(dataset):
            if not re.search("[a-z]", sentence.lower()):
                f.write(sentence)
