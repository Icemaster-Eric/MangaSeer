from os import listdir
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


def get_kanji():
    with open("datasets/japanese/kanji.txt", "r", encoding="utf-8") as f:
        kanji_list = f.readlines()

    return [kanji.strip() for kanji in kanji_list]


def preprocess_sentence(sentence: str):
    for i, c in enumerate(sentence.strip()):
        if c.isnumeric() or c.isspace():
            continue
        break

    return sentence[i:]


def extract_sentences(path):
    with open(path, "r", encoding="utf-8") as f:
        sentences = f.readlines()

    return set(tqdm(
        (preprocess_sentence(sentence) for sentence in sentences),
        total=100000
    ))


def get_news_dataset():
    with open("datasets/japanese/news_dataset.txt", "r", encoding="utf-8") as f:
        sentences = f.readlines()

    return [sentence.strip() for sentence in sentences]


def main():
    conv_dataset = get_conv_dataset()
    news_dataset = get_news_dataset()
    sentence_dataset = set(conv_dataset + news_dataset)
    kanji_list = set(get_kanji())
    missing_kanji = set()

    for kanji in tqdm(kanji_list):
        for sentence in sentence_dataset:
            if kanji in sentence:
                break
        else:
            missing_kanji.add(kanji)

    print(f"Kanji Found: {(len(kanji_list) - len(missing_kanji))/len(kanji_list):.2%}")


if __name__ == "__main__":
    main()
