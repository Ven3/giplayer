import json
import time
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pykeyboard import *

from ui.configwindow import Ui_MainWindow


class WorkerThreader(QThread):
    stop_sign = pyqtSignal(bool)

    def __init__(self, file_path, type):
        super(WorkerThreader, self).__init__()
        self.file_path = file_path
        self.type = type
        self.stop_sign = True


    def run(self):
        time.sleep(2)
        if self.type == "text":
            path = Path(self.file_path)
            json_file_path = self.file_path.replace(path.suffix, ".json")
            json_file = open(json_file_path, "w+", encoding="utf-8")
            music_file = open(self.file_path, "r+", encoding="utf-8")
            keys_lines = music_file.readlines()
            for keys_line in keys_lines:
                if keys_line.startswith("//") or keys_line.startswith("#") or len(keys_line.strip()) == 0:
                    continue
                elif keys_line.startswith("pause="):
                    pause = eval(keys_line.replace("pause=", "").strip())
                    music = {"pause": pause, "keys": []}
                else:
                    keys = keys_line.strip().split(" ")
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
                            subpause = pause * 4
                        elif key.__contains__("+"):
                            subpause = pause * 2
                        music["keys"].append({
                            "key": keypause[0],
                            "pause": subpause
                        })
            text = json.dumps(music)
            json_file.write(text)
            json_file.flush()
            json_file.close()
            self.type = "json"
            self.file_path = json_file_path
        if self.type == "json":
            json_file = open(self.file_path, "r+", encoding="utf-8")
            music = json.loads(json_file.read())
            keys = music["keys"]
            json_file.close()
        for item in keys:
            self.press_keys(item["key"])
            time.sleep(item["pause"])

    def press_keys(self, keys):
        pykey = PyKeyboard()
        pykey.press_keys(keys)

    def stop(self):
        self.terminate()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.work_threader = None
        self.setupUi(self)
        self.btn_selectfile.pressed.connect(self.selectFile)

        self.btn_start.pressed.connect(self.start_play)
        self.btn_stop.pressed.connect(self.stop_play)


    def selectFile(self):
        savePath = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件夹", "./", "*.txt *.json")
        if len(savePath[0]) > 0:
            self.file_path.setText(str(savePath[0]))

    def start_play(self):
        path = Path(self.file_path.text())
        file_path = self.file_path.text()
        if path.suffix == ".json":
            type = "json"
        elif path.suffix == ".txt":
            type = "text"
        self.work_threader = WorkerThreader(file_path, type)
        time.sleep(3)
        self.work_threader.start()

    def stop_play(self):
        self.work_threader.stop()
        self.work_threader.stop_sign = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
