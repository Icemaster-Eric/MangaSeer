import ujson
import sqlite3
from sudachipy import tokenizer, dictionary


# add the json to the file directly?
with open("jmdict_tags.json", "r", encoding="utf-8") as f:
    jmdict_tags: dict[str, str] = ujson.load(f)

with open("kanji.txt", "r", encoding="utf-8") as f:
    kanji: set[str] = set([k.strip() for k in f.readlines()])

with open("pos_tags.json", "r", encoding="utf-8") as f:
    sudachi_to_jmdict: dict[str, str] = ujson.load(f)


class JMDict:
    def __init__(self, jmdict_path: str):
        self.jmdict_connection = sqlite3.connect(jmdict_path)
        self.jmdict_cursor = self.jmdict_connection.cursor()

        self.sudachi_dict = dictionary.Dictionary(dict="core").create()
    
    @staticmethod
    def _get_tags(tags: str) -> list[str]:
        if not tags:
            return []

        return tags.split(",")
    
    @staticmethod
    def tag_text(tag: str) -> str:
        return jmdict_tags.get(tag)

    def lookup(self, text: str, common=True) -> list[dict]:
        """Tokenizes the given string and looks up jmdict/jmnedict definitions for each word

        Args:
            text (str): The text to look up.
            common (bool, optional): Whether to only include common definitions. Defaults to True.

        Returns:
            list[dict]: The tokenized string as a list, along with relevant information.
        """
        output = []

        for morpheme in self.sudachi_dict.tokenize(text, tokenizer.Tokenizer.SplitMode.A):
            pos = set(morpheme.part_of_speech())

            parts_of_speech = [sudachi_to_jmdict.get(p) for p in pos if p in sudachi_to_jmdict]

            token = morpheme.raw_surface()

            if "助詞" in pos: # ignore particles
                output.append({"text": token, "pos": parts_of_speech, "type": None})
                continue

            if not token.isalpha():
                output.append({
                    "text": token,
                    "pos": parts_of_speech,
                    "type": None
                })
                continue

            table = "kanji" if kanji.intersection(set(token)) else "kana"

            words = [{
                "id": word[0],
                "tags": self._get_tags(word[1]),
                "common": bool(word[2])
            } for word in self.jmdict_cursor.execute(
                f"SELECT word_id, tags, common FROM {table} WHERE text = ?",
                (token,)
            ).fetchall()]

            if table == "kanji":
                for word in words:
                    word["reading"] = self.jmdict_cursor.execute(
                        f"SELECT text FROM kana WHERE word_id = ?",
                        (word["id"],)
                    ).fetchone()[0]

            for word in words:
                senses = [
                    {
                        "id": info[0],
                        "dialect": self._get_tags(info[1]),
                        "misc": self._get_tags(info[2]),
                        "info": info[3].replace("\n", "") if info[3] else None,
                        "pos": self._get_tags(info[4]),
                        "field": self._get_tags(info[5]),
                        "gloss": []
                    } for info in self.jmdict_cursor.execute(
                        f"SELECT id, dialect, misc, info, pos, field FROM senses WHERE word_id = ?",
                        (word["id"],)
                    ).fetchall()
                ]

                for sense in senses:
                    for gloss in self.jmdict_cursor.execute(
                        f"SELECT gender, text, lang FROM glossary WHERE sense_id = ?",
                        (sense["id"],)
                    ).fetchall():
                        sense["gloss"].append({
                            "gender": gloss[0],
                            "text": gloss[1],
                            "lang": gloss[2]
                        })

                word["senses"] = senses

            if words:
                output.append({
                    "text": token,
                    "pos": parts_of_speech,
                    "type": "word",
                    "words": [word for word in words if word["common"] or not common]
                })
                continue

            output.append({"text": token, "pos": parts_of_speech, "type": None})

        return output
