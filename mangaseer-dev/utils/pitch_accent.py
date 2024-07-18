import ujson


with open("readings.json", "r", encoding="utf-8") as f:
    readings: dict[str, list[list[str, str]]] = ujson.load(f)


def get_pitch(word: str) -> tuple[tuple[tuple[str, tuple[str]]]] | None:
    word_readings = readings.get(word)

    if not word_readings:
        return

    output = []

    for reading, pitch_accents in word_readings:
        output.append([])
        morae = []

        for char in reading:
            if char in "ゃゅょ":
                morae[-1] += char
            else:
                morae.append(char)

        for pitch_accent in pitch_accents.split(","):
            output[-1].append([])
            pitch_accent = int("".join(c for c in pitch_accent if c.isdigit()))

            for i, mora in enumerate(morae):
                if pitch_accent == 0:
                    if i == 0:
                        position = "low"
                    else:
                        position = "high"
                elif pitch_accent == 1:
                    if i == 0:
                        position = "high"
                    else:
                        position = "low"
                else:
                    if i != 0 and i < pitch_accent + 1:
                        position = "high"
                    else:
                        position = "low"

                output[-1][-1].append((mora, position))
            
            output[-1][-1] = tuple(output[-1][-1])

        output[-1] = tuple(set(output[-1])) # deduplication

    return tuple(output)


if __name__ == "__main__":
    from pprint import pp
    pp(get_pitch("化物"))
