from os import listdir
from PIL import Image, ImageFont, ImageDraw
import ujson
from tqdm import tqdm
from pykakasi import kakasi
from sudachipy import tokenizer, dictionary


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


def needs_furigana(text: str, kanji_set: set[str]) -> bool:
    """Determines whether a string needs furigana or not

    Args:
        text (str): Text to be analyzed
        kanji_set (set[str]): Set of valid kanji characters

    Returns:
        bool: Whether the string needs furigana or not
    """
    return bool(len(kanji_set.intersection(set(text)))) # currently just checks whether there's kanji in the string or not


sudachi_dict = dictionary.Dictionary(dict="full").create()
kks = kakasi()
kanji_set = get_kanji()


def furigana(text):
    for token in sudachi_dict.tokenize(text, tokenizer.Tokenizer.SplitMode.B):
        print(token.normalized_form(), end="")

        if needs_furigana(token.normalized_form(), kanji_set):
            print(f"[{kks.convert(token.normalized_form())[0]['hira']}]", end="")

        print(end="-")
    print("\n")


def test():
    conv_dataset = get_conv_dataset()
    news_dataset = get_news_dataset()
    dataset = conv_dataset.union(news_dataset)


if __name__ == "__main__":
    test()
