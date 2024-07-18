from os import listdir
from random import randint
from multiprocessing.pool import ThreadPool
import ujson
from tqdm import tqdm
from pykakasi import kakasi
from sudachipy import tokenizer, dictionary
from utils import Renderer


def get_conv_dataset() -> set:
    conv_dataset = set()

    for file_name in listdir("manga_datasets/japanese/conv-json"):
        with open(f"manga_datasets/japanese/conv-json/{file_name}", "r", encoding="utf-8") as f:
            for dialogue in ujson.load(f):
                for utterance in dialogue["utterances"]:
                    conv_dataset.add(utterance["utterance"])

    return conv_dataset


def get_kanji() -> set:
    with open("manga_datasets/japanese/kanji.txt", "r", encoding="utf-8") as f:
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
    with open("manga_datasets/japanese/news_dataset.txt", "r", encoding="utf-8") as f:
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


def furigana(text: str, random=False) -> tuple[str, str]:
    """Furigana-izes text

    Args:
        text (str): Text to be furigana-ized
        random (bool, optional): Randomly decide (coin toss) whether to apply furigana. Defaults to False.

    Returns:
        tuple[str, str]: modified text, html string w/ ruby annotations for furigana
    """
    raw = ""
    html = "<p>"

    for token in sudachi_dict.tokenize(text, tokenizer.Tokenizer.SplitMode.A): # erm should probs make sure this split mode is optimal
        token = token.normalized_form()

        if random:
            if randint(0, 1):
                html += token
                raw += token
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

                html += f"<ruby>{original[:len(original)-c]}<rt>{furigana}</rt></ruby>{token[len(original)-c:]}"
                raw += original[:len(original)-c] + token[len(original)-c:]

        else:
            html += token
            raw += token

    html += "</p>"

    return raw, html


def generate_dataset():
    renderer = Renderer()
    conv_dataset = [furigana(sentence.replace("\n", ""), random=True) for sentence in get_conv_dataset()][30000:30010]
    #news_dataset = get_news_dataset()
    #dataset = conv_dataset.union(news_dataset)
    with ThreadPool(processes=2) as pool:
        results = pool.map(renderer.render, conv_dataset)

    results = {v:k for k, v in results}

    with open("sentences.json", "w", encoding="utf-8") as f:
        ujson.dump(results, f)


if __name__ == "__main__":
    generate_dataset()
    """with open("images.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    image_text_pairs = {line.strip().split("|", 1)[0]:line.strip().split("|", 1)[1] for line in lines}
    with open("sentences.json", "w", encoding="utf-8") as f:
        ujson.dump(image_text_pairs, f)"""
    """from PIL import Image

    with open("manga_datasets/ocr/clean_10k/sentences.json", "r", encoding="utf-8") as f:
        sentences = ujson.load(f)

    for image, sentence in list(sentences.items())[:16000]:
        Image.open(f"rendered_images/{image}").save(f"manga_datasets/ocr/clean_10k/train/{image}")
    for image, sentence in list(sentences.items())[16000:]:
        Image.open(f"rendered_images/{image}").save(f"manga_datasets/ocr/clean_10k/valid/{image}")"""
