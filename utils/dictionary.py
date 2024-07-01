import ujson


class JMDict:
    def __init__(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            jmdict_json = ujson.load(f)

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
        jmdict_json = ujson.load(f)

    # do some processing here or whatever
    # I'll probably need a reverse lookup thingy
