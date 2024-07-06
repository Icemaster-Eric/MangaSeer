from typing import Any, Literal
import ujson
import sqlite3
from sudachipy import tokenizer, dictionary
from pprint import pp

# add the json to the file directly?
with open("jmdict_tags.json", "r", encoding="utf-8") as f:
    jmdict_tags = ujson.load(f)

with open("jmnedict_tags.json", "r", encoding="utf-8") as f:
    jmnedict_tags = ujson.load(f)

with open("manga_datasets/japanese/kanji.txt", "r", encoding="utf-8") as f:
    kanji = set([k.strip() for k in f.readlines()])


class JMDict:
    def __init__(self, **dicts: dict[str, tuple[str, dict[str, str]]]):
        self.dicts: dict[str, dict[Literal["connection", "cursor", "tags"], sqlite3.Connection | sqlite3.Cursor | dict[str, str]]] = {
            dict_name: {
                "connection": (connection := sqlite3.connect(dict_path)),
                "cursor": connection.cursor(),
                "tags": dict_info[1]
            } for dict_name, dict_info in dicts.items()
        }
        self.kanji = kanji

        self.sudachi_dict = dictionary.Dictionary(dict="full").create()

    def _search_dicts(
            self,
            queries: dict[str, dict[str, tuple]]
    ) -> list[Any]:
        results = []

        for dict_name, dict_queries in queries.items():
            for query, args in dict_queries.items():
                self.dicts[dict_name]["cursor"].execute(
                    query, args
                )

    def lookup(self, text: str) -> list[dict | str]:
        result = []

        for morpheme in self.sudachi_dict.tokenize(text, tokenizer.Tokenizer.SplitMode.C):
            token = morpheme.normalized_form()

            if not token.isalpha():
                result.append(token)
                continue

            result.append(self._search_dicts(
                {
                    "jmdict": {
                        "SELECT word_id FROM kanji WHERE text = ?": token,
                        "SELECT word_id FROM kana WHERE text = ?": token
                    },
                    "jmnedict": {
                        "SELECT word_id FROM kanji WHERE text = ?": token,
                        "SELECT word_id FROM kana WHERE text = ?": token
                    }
                }
            ))

        return result


def generate_jmdict_sqlite(path: str):
    with open(path, "r", encoding="utf-8") as f:
        jmdict_json: dict = ujson.load(f)
    
    connection = sqlite3.connect("jmdict.db")
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS "kanji" (
	"id" INTEGER NOT NULL UNIQUE,
	"word_id" INTEGER NOT NULL,
	"text" TEXT,
	"tags" TEXT,
	"common" INTEGER,
	PRIMARY KEY("id")
);""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS "kana" (
	"id" INTEGER NOT NULL UNIQUE,
	"word_id" INTEGER NOT NULL,
	"text" TEXT,
	"tags" TEXT,
	"common" INTEGER,
	PRIMARY KEY("id")
);""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS "senses" (
	"id" INTEGER NOT NULL UNIQUE,
    "word_id" INTEGER NOT NULL,
	"field" TEXT,
	"dialect" TEXT,
	"misc" TEXT,
	"info" TEXT,
	"pos" TEXT,
	PRIMARY KEY("id"),
	FOREIGN KEY ("id") REFERENCES "glossary"("sense_id")
	ON UPDATE CASCADE ON DELETE CASCADE
);""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS "glossary" (
	"id" INTEGER NOT NULL UNIQUE,
	"sense_id" INTEGER NOT NULL,
	"gender" TEXT,
	"text" TEXT,
	"lang" TEXT,
	PRIMARY KEY("id")
);""")

    for word in jmdict_json["words"]:
        word_id = int(word["id"])

        for kanji in word["kanji"]:
            cursor.execute(
                "INSERT INTO kanji (word_id, text, tags, common) VALUES (?, ?, ?, ?)",
                (
                    word_id,
                    kanji["text"],
                    ",".join(kanji["tags"]),
                    int(kanji["common"])
                )
            )

        for kana in word["kana"]:
            cursor.execute(
                "INSERT INTO kana (word_id, text, tags, common) VALUES (?, ?, ?, ?)",
                (
                    word_id,
                    kana["text"],
                    ",".join(kana["tags"]),
                    int(kana["common"])
                )
            )

        for sense in word["sense"]:
            cursor.execute(
                "INSERT INTO senses (word_id, field, dialect, misc, info, pos) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    word_id,
                    ",".join(sense["field"]),
                    ",".join(sense["dialect"]),
                    ",".join(sense["misc"]),
                    "\n".join(sense["info"]),
                    ",".join(sense["partOfSpeech"])
                )
            )

            sense_id = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]

            for gloss in sense["gloss"]:
                cursor.execute(
                    "INSERT INTO glossary (sense_id, gender, text, lang) VALUES (?, ?, ?, ?)",
                    (
                        sense_id,
                        gloss["gender"],
                        gloss["text"],
                        gloss["lang"]
                    )
                )

        connection.commit()


def generate_jmnedict_sqlite(path: str):
    with open(path, "r", encoding="utf-8") as f:
        jmnedict_json: dict = ujson.load(f)
    
    connection = sqlite3.connect("jmnedict.db")
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS "kana" (
	"id" INTEGER NOT NULL UNIQUE,
	"word_id" INTEGER NOT NULL,
	"text" TEXT,
	"tags" TEXT,
	PRIMARY KEY("id")
);""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS "kanji" (
	"id" INTEGER NOT NULL UNIQUE,
	"word_id" INTEGER NOT NULL,
	"text" TEXT,
	"tags" TEXT,
	PRIMARY KEY("id")
);""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS "translations" (
	"id" INTEGER NOT NULL UNIQUE,
	"word_id" INTEGER,
	"text" TEXT,
	"type" TEXT,
	PRIMARY KEY("id")	
);""")

    for word in jmnedict_json["words"]:
        word_id = int(word["id"])

        for kanji in word["kanji"]:
            cursor.execute(
                "INSERT INTO kanji (word_id, text, tags) VALUES (?, ?, ?)",
                (
                    word_id,
                    kanji["text"],
                    ",".join(kanji["tags"])
                )
            )

        for kana in word["kana"]:
            cursor.execute(
                "INSERT INTO kana (word_id, text, tags) VALUES (?, ?, ?)",
                (
                    word_id,
                    kana["text"],
                    ",".join(kana["tags"])
                )
            )

        for translation in word["translation"]:
            cursor.execute(
                "INSERT INTO translations (word_id, text, type) VALUES (?, ?, ?)",
                (
                    word_id,
                    ",".join(translation["type"]),
                    "\n".join([t["text"] for t in translation["translation"]])
                )
            )

        connection.commit()


if __name__ == "__main__":
    jmdict = JMDict(
        jmdict=("jmdict.db", jmdict_tags),
        jmnedict=("jmnedict.db", jmnedict_tags)
    )

    pp(jmdict.lookup("私がよく聴くのは西野カナの曲です。彼女の歌の歌詞がとても好きなのです。"))
