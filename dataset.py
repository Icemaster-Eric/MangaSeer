from os import listdir
from random import randint
from multiprocessing import Pool
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


def furigana(text: str, random=False) -> str:
    """Furigana-izes text

    Args:
        text (str): Text to be furigana-ized
        random (bool, optional): Randomly decide (coin toss) whether to apply furigana. Defaults to False.

    Returns:
        str: Html string w/ ruby annotations for furigana
    """
    output = "<p>"

    for token in sudachi_dict.tokenize(text, tokenizer.Tokenizer.SplitMode.A): # erm should probs make sure this split mode is optimal
        token = token.normalized_form()

        if random:
            if randint(0, 1):
                output += token
                continue

        if needs_furigana(token):
            for result in kks.convert(token):
                original = result["orig"]
                furigana = result["hira"]

                if not needs_furigana(original):
                    continue

                c = 0
                _original = original
                while furigana[-1] == _original[-1]:
                    furigana = furigana[:-1]
                    _original = _original[:-1]
                    c += 1

                output += f"<ruby>{original[:len(original)-c]}<rt>{furigana}</rt></ruby>{token[len(original)-c:]}"

        else:
            output += token

    output += "</p>"

    return output


def generate_dataset():
    renderer = Renderer()
    conv_dataset = [furigana(sentence, random=True) for sentence in get_conv_dataset()]
    #news_dataset = get_news_dataset()
    #dataset = conv_dataset.union(news_dataset)
    pool = Pool(4)
    pool.map(renderer.render, conv_dataset)


if __name__ == "__main__":
    #generate_dataset()
    pass
