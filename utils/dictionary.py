import ujson
import sqlite3
from sudachipy import tokenizer, dictionary
from pprint import pp

# add the json to the file directly?
with open("jmdict_tags.json", "r", encoding="utf-8") as f:
    jmdict_tags: dict[str, str] = ujson.load(f)

with open("jmnedict_tags.json", "r", encoding="utf-8") as f:
    jmnedict_tags: dict[str, str] = ujson.load(f)

with open("manga_datasets/japanese/kanji.txt", "r", encoding="utf-8") as f:
    kanji: set[str] = set([k.strip() for k in f.readlines()])


class JMDict:
    def __init__(self, jmdict_path: str, jmnedict_path: str):
        self.jmdict_connection = sqlite3.connect(jmdict_path)
        self.jmdict_cursor = self.jmdict_connection.cursor()

        self.jmnedict_connection = sqlite3.connect(jmnedict_path)
        self.jmnedict_cursor = self.jmnedict_connection.cursor()

        self.sudachi_dict = dictionary.Dictionary(dict="full").create()
    
    @staticmethod
    def _get_tags(tags: str, jmdict: bool | None = None) -> list[str]:
        if not tags:
            return []

        match jmdict:
            case None:
                return tags.split(",")
            case True:
                return [jmdict_tags[tag] for tag in tags.split(",")]
            case False:
                return [jmnedict_tags[tag] for tag in tags.split(",")]

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
            #print(morpheme.raw_surface(), morpheme.part_of_speech())
            pos = set(morpheme.part_of_speech())

            if "助詞" in pos: # ignore particles
                #print("ignored")
                continue

            token = morpheme.raw_surface()

            if not token.isalpha():
                output.append({
                    "text": token,
                    "type": None
                })
                continue

            table = "kanji" if kanji.intersection(set(token)) else "kana"

            if pos.intersection({"固有名詞", "人名"}): # proper noun
                words = [{
                    "id": word[0],
                    "tags": self._get_tags(word[1], jmdict=False)
                } for word in self.jmnedict_cursor.execute(
                    f"SELECT word_id, tags FROM {table} WHERE text = ?",
                    (token,)
                ).fetchall()]

                if table == "kanji":
                    for word in words:
                        word["reading"] = self.jmnedict_cursor.execute(
                            f"SELECT text FROM kana WHERE word_id = ?",
                            (word["id"],)
                        ).fetchone()[0]

                for word in words:
                    word["translations"] = [
                        {
                            "text": info[0].replace("\n", "") if info[0] else None,
                            "type": self._get_tags(info[1], jmdict=False)
                        } for info in self.jmnedict_cursor.execute(
                            f"SELECT text, type FROM translations WHERE word_id = ?",
                            (word["id"],)
                        ).fetchall()
                    ]

                if words:
                    output.append({
                        "text": token,
                        "type": "name",
                        "words": [word for word in words]
                    })
                    continue

            words = [{
                "id": word[0],
                "tags": self._get_tags(word[1], jmdict=True),
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
                        "dialect": self._get_tags(info[1], jmdict=True),
                        "misc": self._get_tags(info[2], jmdict=True),
                        "info": info[3].replace("\n", "") if info[3] else None,
                        "pos": self._get_tags(info[4], jmdict=True),
                        "field": self._get_tags(info[5], jmdict=True),
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
                    "type": "word",
                    "words": [word for word in words if word["common"] or not common]
                })
                continue

            output.append({"text": token, "type": None})

        return output


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
                "INSERT INTO translations (word_id, type, text) VALUES (?, ?, ?)",
                (
                    word_id,
                    ",".join(translation["type"]),
                    "\n".join([t["text"] for t in translation["translation"]])
                )
            )

        connection.commit()


if __name__ == "__main__":
    jmdict = JMDict("jmdict.db", "jmnedict.db")

    output = jmdict.lookup("私がよく聴くのは西野カナの曲です。彼女の歌の歌詞がとても好きなのです。")
    pp(output)
