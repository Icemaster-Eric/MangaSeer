import ujson
import sqlite3


class JMDict:
    def __init__(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            jmdict_json = ujson.load(f)
        
        self.tags = jmdict_json["tags"]

    def lookup(self, text: str) -> list[dict]:
        return [
            {
                "word": "",
                "type": "",
                "definitions": (
                    "definition a",
                    "definition b"
                )
            }
        ]


if __name__ == "__main__":
    with open("manga_datasets/japanese/jmdict-eng-3.5.0.json", "r", encoding="utf-8") as f:
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

    for word in jmdict_json["words"][:5]:
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

            sense_id = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]\

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
