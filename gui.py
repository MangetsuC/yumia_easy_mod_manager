from tkinter import Tk, Listbox, StringVar, Frame, Label, Button, filedialog, messagebox
import functions
import toml, os

class Yumia_mod_manager_gui(Tk):
    def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.title("Yumia esay mod manager")

        self.config = None
        self.yumia_root_path = None

        self.this_mod_name = None
        
        
        self.row_interact = Frame(self)
        self.mods_column = Frame(self.row_interact)
        self.conflict_mods_column = Frame(self.row_interact)
        self.btn_column = Frame(self.row_interact)
        

        #mods
        self.mods_label = Label(self.mods_column, text="mods")
        #self.mods_label.config(text="test")

        self.mod_list_ori = []
        self.mods_list = StringVar()

        self.mods_listbox = Listbox(self.mods_column, listvariable=self.mods_list)
        self.mods_label.pack(side="top", fill="x")
        self.mods_listbox.pack(side="top", fill="x")

        #conflict
        self.conflict_mods_label = Label(self.conflict_mods_column, text="conflict_mods")

        self.conflict_list = StringVar()
        self.conflict_mod_listbox = Listbox(self.conflict_mods_column, listvariable=self.conflict_list)
        self.conflict_mods_label.pack(side="top", fill="x")
        self.conflict_mod_listbox.pack(side="top", fill="x")

        #buttons
        self.btn_chose_game_path = Button(self.btn_column, text="Choose game path", command=self.set_yumia_game_path)
        self.btn_import_mod = Button(self.btn_column, text="Import mod file", command=self.import_mod)
        self.btn_enable_or_disable = Button(self.btn_column, text="Waiting choose", command=self.enable_or_disable_mod)
        self.btn_mod_folder = Button(self.btn_column, text="Open mods folder", command=self.open_folder)
        self.btn_refresh_mods = Button(self.btn_column, text="Refresh mods list", command=self.manual_refresh_mods_list)

        self.btn_chose_game_path.pack(side="top", fill="x")
        self.btn_import_mod.pack(side="top", fill="x")
        self.btn_enable_or_disable.pack(side="top", fill="x")
        self.btn_mod_folder.pack(side="top", fill="x")
        self.btn_refresh_mods.pack(side="top", fill="x")

        #yumia_path
        self.label_yumia_path = Label(self, text="game path not found")

        self.mods_column.pack(side="left", fill="y")
        self.conflict_mods_column.pack(side="left", fill="y")
        self.btn_column.pack(side="left", fill="y")


        self.row_interact.pack(side="top", fill="x")
        self.label_yumia_path.pack(side="top", fill="x")

        self.mods_listbox.bind("<ButtonRelease-1>", self.on_click_mod)


        self.refresh_mods_list()

        self.load_toml()
        if self.yumia_root_path == None:
            messagebox.showinfo("info", "Please choose the game file first")
            self.set_yumia_game_path()

        functions.back_up_rdb_rdx(self.yumia_root_path)
        self.show_game_path()

    def show_game_path(self):
        #self.label_yumia_path.config(text=f"game path: {self.yumia_root_path}") #too long to show
        self.label_yumia_path.config(text=f"game path found")

    def load_toml(self):
        if not os.path.exists("./config.toml"):
            f = open("./config.toml", "w")
            f.close()

        with open("./config.toml", "r") as f:
            self.config = toml.load(f)

        self.yumia_root_path = self.config.get("yumia_root_path", None)

    def dump_toml(self):
        with open("./config.toml", "w") as f:
            toml.dump(self.config, f)

    def refresh_mods_list(self):
        self.mod_list_ori = functions.get_all_mods_list()
        tmp_list = []
        for mod in self.mod_list_ori:
            if functions.check_mod_state(mod):
                tmp_list.append(f"{mod}[enabled]")
            else:
                tmp_list.append(f"{mod}")
        self.mods_list.set(tmp_list)

    def refresh_conflict_list(self, this_mod_name):
        self.conflict_list.set(functions.get_conflict_mods(this_mod_name))


    def on_click_mod(self, event):
        self.this_mod_name = self.mod_list_ori[self.mods_listbox.curselection()[0]]

        self.refresh_conflict_list(self.this_mod_name)

        if functions.check_mod_state(self.this_mod_name):
            self.btn_enable_or_disable.config(text="Disable this mod")
        else:
            self.btn_enable_or_disable.config(text="Enable this mod")

    def enable_or_disable_mod(self):
        if self.this_mod_name == None:
            print("No mod selected")
            return None
        if self.yumia_root_path == None:
            print("Cannot find yumia game path")
            return None
        
        if functions.check_mod_state(self.this_mod_name):
            #disable
            functions.disable_mod(self.yumia_root_path, self.this_mod_name)
            self.btn_enable_or_disable.config(text="Enable this mod")
        else:
            #enable
            functions.enable_mod(self.yumia_root_path, self.this_mod_name)
            self.btn_enable_or_disable.config(text="Disable this mod")

        self.refresh_mods_list()

    def import_mod(self):
        mod_path = filedialog.askopenfilename(title="select mod archive file",
                                           filetypes=[("mod archive file", "*.7z *.zip")])
        
        if mod_path:
            functions.load_mods_archive_file(mod_path)
            self.refresh_mods_list()
            self.refresh_conflict_list(self.this_mod_name)

    def set_yumia_game_path(self):
        tmp_path = filedialog.askopenfilename(title="select Atelier_Yumia.exe",
                                           filetypes=[("game file", "Atelier_Yumia.exe")])
        
        if tmp_path:
            self.yumia_root_path = os.path.dirname(tmp_path)
            
            self.config.update(dict(yumia_root_path = self.yumia_root_path))
            self.dump_toml()
            self.show_game_path()
            functions.back_up_rdb_rdx(self.yumia_root_path)

    def open_folder(self):
        os.startfile(f"\"{os.getcwd()}/mods\"")

    def manual_refresh_mods_list(self):
        self.refresh_mods_list()

if __name__ == "__main__":
    pass

