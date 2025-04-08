from tkinter import Tk, Listbox, StringVar, Frame, Label, Button, filedialog, messagebox, Entry, simpledialog, Text
from tkinter.scrolledtext import ScrolledText
import functions
import fdata_functions
import toml, os, sys
import threading

class Yumia_mod_manager_gui(Tk):
    def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.title("Yumia easy mod manager")
        
        if hasattr(sys, '_MEIPASS'):
            if os.path.exists(f"{sys._MEIPASS}/assets/ico.ico"):
                self.iconbitmap(f"{sys._MEIPASS}/assets/ico.ico")
        else:
            if os.path.exists("./ico.ico"):
                self.iconbitmap("./ico.ico")

        self.config = None
        self.yumia_root_path = None
        self.is_ignore_md5_check = None

        self.this_mod_name = None
        self.submod_name = None #include prefix "0x"

        #download tool state
        self.is_download = False
        self.is_download_finish = False
        
        
        self.row_interact = Frame(self)
        self.mods_column = Frame(self.row_interact)
        self.conflict_mods_column = Frame(self.row_interact)
        self.btn_column = Frame(self.row_interact)
        

        #mods
        self.mods_label = Label(self.mods_column, text="mods")
        #self.mods_label.config(text="test")

        self.mod_list_ori = []
        self.mods_list = StringVar()

        self.mods_listbox = Listbox(self.mods_column, listvariable=self.mods_list, exportselection=False) #exportselection=False disable the auto copy and enable multi selected
        self.mods_label.pack(side="top", fill="x", expand=True)
        self.mods_listbox.pack(side="top", fill="x", expand=True)

        self.mods_listbox.bind("<ButtonRelease-1>", self.on_click_mod)

        #conflict
        self.conflict_mods_label = Label(self.conflict_mods_column, text="conflict_mods")

        self.conflict_list = StringVar()
        self.conflict_mod_listbox = Listbox(self.conflict_mods_column, listvariable=self.conflict_list, exportselection=False)
        self.conflict_mods_label.pack(side="top", fill="x")
        self.conflict_mod_listbox.pack(side="top", fill="x")

        #buttons
        self.btn_chose_game_path = Button(self.btn_column, text="Choose game path", command=self.set_yumia_game_path)
        self.btn_import_mod = Button(self.btn_column, text="Import mod file", command=self.import_mod)
        self.btn_enable_or_disable = Button(self.btn_column, text="Waiting choose", command=self.enable_or_disable_mod, state="disabled")
        self.btn_mod_folder = Button(self.btn_column, text="Open mods folder", command=self.open_folder)
        self.btn_refresh_mods = Button(self.btn_column, text="Refresh mods list", command=self.manual_refresh_mods_list)

        self.btn_chose_game_path.pack(side="top", fill="x")
        self.btn_import_mod.pack(side="top", fill="x")
        self.btn_enable_or_disable.pack(side="top", fill="x")
        self.btn_mod_folder.pack(side="top", fill="x")
        self.btn_refresh_mods.pack(side="top", fill="x")

        #entry
        self.entry_hash = Entry(self.btn_column)
        self.entry_hash.pack(side="top", fill="x")
        self.entry_hash.insert(0, "fdata hex code")

        #hash_btn
        self.btn_reset_fdata_hash = Button(self.btn_column, text="Reset hash", command=self.reset_fdata_hash)
        self.btn_reset_fdata_hash.pack(side="top", fill="x")

        #yumia_path
        self.label_log = Label(self, text="Log")

        #stdout
        self.text_stdout = ScrolledText(self, state="disabled", height=5)

        #outer frame pack
        self.mods_column.pack(side="left", fill="both", expand=True)
        self.conflict_mods_column.pack(side="left", fill="y")
        self.btn_column.pack(side="left", fill="y")


        self.row_interact.pack(side="top", fill="x")
        self.label_log.pack(side="top", fill="x")
        self.text_stdout.pack(side="top", fill="both" ,expand=True)

        self.load_toml()

        self.after(1, self.after_gui_init)
        self.after(10, self.yumia_mod_insert_into_rdb_tool_check)

    def download_yumia_mod_insert_into_rdb_tool(self):
        while self.is_ignore_md5_check == None:
            pass
        functions.download_yumia_mod_insert_into_rdb_tool(self.is_ignore_md5_check)
        self.is_download_finish = True

    def yumia_mod_insert_into_rdb_tool_check(self):
        if not self.is_download:
            tmp_thread = threading.Thread(target=self.download_yumia_mod_insert_into_rdb_tool)
            tmp_thread.start()
            self.is_download = True
        if not self.is_download_finish:
            self.after(100, self.yumia_mod_insert_into_rdb_tool_check)
        else:
            self.btn_enable_or_disable.config(state="normal")
        

    def after_gui_init(self):
        functions.mk_mods_folder()

        self.refresh_mods_list()

        if self.yumia_root_path == None:
            messagebox.showinfo("info", "Please choose the game file first")
            self.set_yumia_game_path()

        functions.back_up_rdb_rdx(self.yumia_root_path)
        self.show_game_path()

    def get_log_text(self) ->Text:
        return self.text_stdout

    def show_game_path(self):
        print(f"Game path: {self.yumia_root_path}")

    def load_toml(self):
        if not os.path.exists("./config.toml"):
            f = open("./config.toml", "w")
            f.close()

        with open("./config.toml", "r") as f:
            self.config = toml.load(f)

        self.yumia_root_path = self.config.get("yumia_root_path", None)
        self.is_ignore_md5_check = self.config.get("ignore_md5_check", False)

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

            is_has_submods, submods = functions.check_has_sub_mod(mod)
            if is_has_submods:
                #add submods hex under the top mod
                for submod in submods:
                    tmp_list.append(f"  |{os.path.splitext(os.path.basename(submod))[0]}")
        self.mods_list.set(tmp_list)
        
    def hex_reset_refresh_mod_list(self):
        tmp_sel_index = self.mods_listbox.curselection()
        if len(tmp_sel_index) > 1:
            tmp_sel_index = tmp_sel_index[0]
        else:
            tmp_sel_index = -1
        self.refresh_mods_list()
        if tmp_sel_index >= 0:
            self.mods_listbox.select_set(tmp_sel_index)

    def refresh_conflict_list(self, this_mod_name, submod_name = None):
        self.conflict_list.set(functions.get_conflict_mods(this_mod_name, submod_name))

    def convert_StringVar_to_list(self, stringvar:StringVar) -> list[str]:
        list_str = stringvar.get()[1:-1]
        tmp_list = list_str.split(",") #应该定位单引号然后取出内容
        ans_list = []
        for each_str in tmp_list:
            l_qm_index = each_str.find("'")
            r_qm_index = each_str.rfind("'")
            if l_qm_index >= 0  and r_qm_index >= 0 and l_qm_index < r_qm_index:
                ans_list.append(each_str[l_qm_index+1:r_qm_index])
        return ans_list

    def on_click_mod(self, event):
        if len(self.mods_listbox.curselection()) == 0:
            return 
        tmp_mods_list = self.convert_StringVar_to_list(self.mods_list)
        tmp_mod_name:str = tmp_mods_list[self.mods_listbox.curselection()[0]]
        tmp_real_modified_mod:str = tmp_mod_name
        self.submod_name = None

        if "|" in tmp_mod_name:
            #是临时列出的子模组
            self.submod_name = tmp_mod_name.strip(" |")
            for tmp_i in range(self.mods_listbox.curselection()[0],-1, -1):
                if "|" not in tmp_mods_list[tmp_i]:
                    tmp_real_modified_mod:str = tmp_mods_list[tmp_i]
                    break

        self.this_mod_name = tmp_real_modified_mod.replace("[enabled]", "")


        self.refresh_conflict_list(self.this_mod_name, self.submod_name)

        self.show_this_fdata_hex(self.this_mod_name, self.submod_name)

        if functions.check_mod_state(self.this_mod_name):
            self.btn_enable_or_disable.config(text="Disable this mod")
        else:
            self.btn_enable_or_disable.config(text="Enable this mod")

    def enable_or_disable_mod(self):
        if self.this_mod_name == None:
            messagebox.showerror("Error", "No mod selected.")
            print("No mod selected")
            return None
        if self.yumia_root_path == None:
            messagebox.showerror("Error", "Cannot find yumia game path.")
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
                                           filetypes=[("mod archive file", "*.7z *.zip"), ("mod fdata file", "*.fdata")])
        
        is_full_mode = True
        if mod_path:
            if ".fdata" in mod_path:
                mod_name = simpledialog.askstring("mod name", "enter your mod name here")
                if mod_name != None:
                    mod_name = mod_name.strip(" ") #delete space
                    functions.cp_fdata(mod_path, mod_name)
                    is_full_mode = False
            else:
                status = functions.load_mods_archive_file(mod_path)
                if status != None:
                    is_full_mode = status[0]
                    mod_name = status[1]

            if not is_full_mode:
                fdata_paths = functions.find_fdatas(mod_name)
                if fdata_paths != []:
                    for fdata_path in fdata_paths:
                        hex_code = os.path.splitext(os.path.basename(fdata_path))[0]
                        if len(hex_code) > 2:
                            if hex_code[0:2] == "0x" or hex_code[0:2] == "0X":
                                hex_code = hex_code[2:]
                        fdata_functions.generate_yumiamod_json(hex_code, fdata_path, "./backup/root.rdb", f"./mods/{mod_name}")

            self.refresh_mods_list()
            self.on_click_mod(None)
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

    def show_this_fdata_hex(self, mod_name, submod_name = None):
        self.btn_reset_fdata_hash.config(state="normal")
        fdata_hex = None
        if submod_name == None:
            is_multi_fdata_mod = functions.check_has_sub_mod(mod_name)[0]
            if is_multi_fdata_mod:
                fdata_hex = "multi-fdata"
                self.btn_reset_fdata_hash.config(state="disabled")
            else:
                fdata_paths = functions.find_fdatas(mod_name)
                if fdata_paths != []:
                    fdata_hex = (os.path.splitext(os.path.basename(fdata_paths[0]))[0])[2:]
        else:
            fdata_hex = submod_name[2:]
        if fdata_hex != None:
            self.entry_hash.delete(0, 'end')
            self.entry_hash.insert(0, fdata_hex)
        
    def reset_fdata_hash(self):
        if functions.check_mod_state(self.this_mod_name):
            messagebox.showerror("Error", "Please disable this mod first.")
            print("Please disable this mod first")
            return 
        target_hex_code = self.entry_hash.get()
        if len(target_hex_code) == 8:
            try:
                int(str(target_hex_code), 16)
            except ValueError:
                messagebox.showerror("Error", "It not a valid hex code. Sample: 88888888")
                print("Not a valid hex code")
                return
            #check submod first
            tmp_submod_file_name = f"{self.submod_name}.fdata" if self.submod_name != None else None
            tmp_submod_file_yumiamodjson_name = f"{self.submod_name}.yumiamod.json" if self.submod_name != None else None
            fdata_paths = functions.find_fdatas(self.this_mod_name, tmp_submod_file_name)
            if fdata_paths != []:
                new_fdata_path = f"{os.path.dirname(fdata_paths[0])}/0x{target_hex_code}.fdata"
                os.rename(fdata_paths[0], new_fdata_path)

                yumiamod_json_path = functions.find_yumiamod_json(self.this_mod_name, tmp_submod_file_yumiamodjson_name)
                if yumiamod_json_path != None:
                    os.remove(yumiamod_json_path)

                fdata_functions.generate_yumiamod_json(target_hex_code, new_fdata_path, "./backup/root.rdb", f"./mods/{self.this_mod_name}")

                #self.hex_reset_refresh_mod_list()
                self.refresh_mods_list()
                self.on_click_mod(None)
        
        else:
            messagebox.showerror("Error", "Error hex code len.")
            print("Error hex code len")



if __name__ == "__main__":
    pass

