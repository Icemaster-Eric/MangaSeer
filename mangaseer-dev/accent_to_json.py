import ujson


with open("accents.txt", "r", encoding="utf-8") as f:
    accents = f.readlines()


json_obj = {}


for accent in accents:
    word, reading, pitch = accent.strip().split("\t")
    if word in json_obj:
        json_obj[word].append([reading, pitch])
    else:
        json_obj[word] = [[reading, pitch]]


with open("readings.json", "w", encoding="utf-8") as f:
    ujson.dump(json_obj, f)
