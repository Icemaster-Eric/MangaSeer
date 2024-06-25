from os import listdir
from PIL import Image, ImageFont, ImageDraw
import ujson
from tqdm import tqdm
from pykakasi import kakasi
from sudachipy import tokenizer, dictionary
from utils import Renderer


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


def needs_furigana(text: str) -> bool:
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
renderer = Renderer()


def furigana(text: str) -> str:
    """Furigana-izes text

    Args:
        text (str): the text to be furigana-ized

    Returns:
        str: html string w/ ruby annotations for furigana
    """
    output = "<p>"

    for token in sudachi_dict.tokenize(text, tokenizer.Tokenizer.SplitMode.A): # erm should probs make sure this split mode is optimal
        token = token.normalized_form()

        if needs_furigana(token):
            for result in kks.convert(token):
                original = result["orig"]
                furigana = result["hira"]

                if not needs_furigana(original):
                    continue

                c = 0
                while furigana[-1] == original[-1]:
                    furigana = furigana[:-1]
                    c += 1

                output += f"<ruby>{original[:len(original)-c]}<rt>{furigana}</rt></ruby>{token[len(original)-c:]}"

        else:
            output += token

    output += "</p>"

    return output


def test():
    conv_dataset = get_conv_dataset()
    #news_dataset = get_news_dataset()
    #dataset = conv_dataset.union(news_dataset)
    print(furigana(conv_dataset.pop()))


if __name__ == "__main__":
    test()
