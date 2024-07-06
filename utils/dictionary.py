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
    def __init__(self, jmdict_path: str, jmnedict_path: str):
        self.jmdict_connection = sqlite3.connect(jmdict_path)
        self.jmdict_cursor = self.jmdict_connection.cursor()

        self.jmnedict_connection = sqlite3.connect(jmnedict_path)
        self.jmnedict_cursor = self.jmnedict_connection.cursor()

        self.jmdict_tags = jmdict_tags
        self.jmnedict_tags = jmnedict_tags
        self.kanji = kanji

        self.sudachi_dict = dictionary.Dictionary(dict="full").create()

    def lookup(self, text: str) -> list[dict | str]:
        result: list[dict | str] = []

        for morpheme in self.sudachi_dict.tokenize(text, tokenizer.Tokenizer.SplitMode.C):
            token = morpheme.normalized_form()

            if not token.isalpha():
                result.append(token)
                continue

            print(self.jmdict_cursor.execute("SELECT word_id FROM kanji WHERE text = ?").fetchall())
            print(self.jmdict_cursor.execute("SELECT word_id FROM kana WHERE text = ?").fetchall())

            result.append()

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
    jmdict = JMDict("jmdict.db", "jmnedict.db")

    pp(jmdict.lookup("私がよく聴くのは西野カナの曲です。彼女の歌の歌詞がとても好きなのです。"))
