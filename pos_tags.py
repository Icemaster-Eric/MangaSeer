# script to find all of sudachidict's part of speech tags by brute force and find frequencies for each
import ujson
import os
from sudachipy import tokenizer, dictionary
from collections import Counter
from pprint import pp


sentences = set()
pos_tags = []


for topic in os.listdir("manga_datasets/japanese/conv-json"):
    with open(f"manga_datasets/japanese/conv-json/{topic}", "r", encoding="utf-8") as f:
        raw = ujson.load(f)

    for conv in raw:
        for utterances in conv["utterances"]:
            sentences.add(utterances["utterance"])


sudachi_dict = dictionary.Dictionary(dict="full").create()

for sentence in sentences:
    for morpheme in sudachi_dict.tokenize(sentence, tokenizer.Tokenizer.SplitMode.A):
        for pos in morpheme.part_of_speech():
            if pos != "*":
                pos_tags.append(pos)


count = Counter(pos_tags)

pp(count.most_common(n=50))
