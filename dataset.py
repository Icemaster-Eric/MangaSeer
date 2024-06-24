from os import listdir
from PIL import Image, ImageFont, ImageDraw
import ujson


def main():
    conv_dataset = []

    for file_name in listdir("datasets/dialogue/conv-json"):
        with open(f"datasets/dialogue/conv-json/{file_name}", "r", encoding="utf-8") as f:
            for dialogue in ujson.load(f):
                for utterance in dialogue["utterances"]:
                    conv_dataset.append(utterance["utterance"])


if __name__ == "__main__":
    main()