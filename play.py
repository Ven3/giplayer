import json
import time

from pykeyboard import *


def convert_to_json(filePath: str):
    lines = open(filePath, "r+", encoding="utf-8").readlines()
    jsonFile = open(filePath.replace(".txt", ".json"), "w+", encoding="utf-8")
    pause = 1 / 4
    music = {}
    for line in lines:
        if line.startswith("//") or line.startswith("#") or len(line.strip()) == 0:
            continue
        elif line.startswith("pause="):
            pause = eval(line.replace("pause=", "").strip())
            music = {"pause": pause, "keys": []}
        else:
            keys = line.strip().split(" ")
            for key in keys:
                keypause = key.strip().split("/")
                subpause = pause
                if len(keypause) > 1:
                    subpause = pause / eval(keypause[1])
                elif key.__contains__("-"):
                    subpause = pause / 2
                elif key.__contains__("_"):
                    subpause = pause / 4
                elif key.__contains__(">"):
                    subpause = pause * 3
                elif key.__contains__("+"):
                    subpause = pause * 2
                music["keys"].append({
                    "key": keypause[0],
                    "pause": subpause
                })
    text = json.dumps(music)
    jsonFile.write(text)
    jsonFile.flush()
    jsonFile.close()


def press_keys(keys):
    keyboard = PyKeyboard()
    keyboard.press_keys(keys)


def play(musicfile):
    file = open(musicfile)
    music_config = json.load(file)
    for item in music_config["keys"]:
        press_keys(item["key"])
        time.sleep(item["pause"])


if __name__ == '__main__':

    fileName = "./examples/诀别书.txt"
    if fileName.endswith(".txt"):
        convert_to_json(fileName)
        fileName = fileName.replace(".txt", ".json")
    time.sleep(3)
    play(fileName)
