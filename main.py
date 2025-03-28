from gui import Yumia_mod_manager_gui
from tkinter import Text
from tkinter import END as TKEND
import time
import sys, os

class Text_stdout_handler:
    def __init__(self, target_text:Text):
        self.text = target_text
        if not os.path.exists("./log.log"):
            f = open("./log.log", "w")
            f.close()

    def write(self, text):
        if text == "":
            return
        
        if text == "\n":
            prefix = ""
        else:
            tmp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            prefix = f"[{tmp_time}]"
        #tmp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open("./log.log", "a") as f:
            f.write(f"{prefix}{text}")

        self.text.config(state="normal")
        #tmp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.text.insert(TKEND, f"{prefix}{text}")
        self.text.see(TKEND)
        self.text.config(state="disabled")




if __name__ == "__main__":
    root = Yumia_mod_manager_gui()

    text_stdout_handler = Text_stdout_handler(root.get_log_text())
    sys.stdout = text_stdout_handler
    sys.stderr = text_stdout_handler

    #root.after_gui_init()
    root.mainloop()








