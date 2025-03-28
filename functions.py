# 方法二：使用requests库
# -*- coding:utf-8 -*-
import requests
from requests.packages import urllib3
import os
import zipfile, py7zr
from shutil import copy

if not os.path.exists("./yumia_mod_insert_into_rdb.exe"):
    urllib3.disable_warnings()
    url = 'https://github.com/eArmada8/yumia_fdata_tools/releases/download/v1.0.0/yumia_mod_insert_into_rdb.exe'
    # 当把get函数的stream参数设置成False时，
    # 它会立即开始下载文件并放到内存中，如果文件过大，有可能导致内存不足。

    # 当把get函数的stream参数设置成True时，它不会立即开始下载，
    # 使用iter_content或iter_lines遍历内容或访问内容属性时才开始下载
    print("Start download yumia_mod_insert_into_rdb.exe from eArmada8")
    r = requests.get(url, stream=True, verify=False)
    f = open("./yumia_mod_insert_into_rdb.exe", "wb")
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
            f.flush()

    f.close()


if not os.path.exists("./mods"):
    os.mkdir("./mods")

def cp_fdata(file_path, mod_name):
    if os.path.exists(file_path):
        if not os.path.exists(f"./mods/{mod_name}"):
            os.mkdir(f"./mods/{mod_name}")
        copy(file_path, f"./mods/{mod_name}/{os.path.basename(file_path)}")

def load_mods_archive_file(file_path) -> list[bool|str]|None:
    mod_name = os.path.splitext(os.path.basename(file_path))[0]
    is_full_mod = False

    if ".7z" in file_path:
        a_f = py7zr.SevenZipFile(file_path, mode='r')
        
        content_list = a_f.namelist()
        yumiamod_json_path = None
        fdata_path = None
        for each_file_name in content_list:
            if ".yumiamod.json" in each_file_name:
                yumiamod_json_path = each_file_name
            elif ".fdata" in each_file_name:
                fdata_path = each_file_name
            
        if fdata_path != None:
            if yumiamod_json_path != None:
                a_f.extract(path=f"./mods/{mod_name}", targets=[yumiamod_json_path, fdata_path])
                is_full_mod = True
            else:
                a_f.extract(path=f"./mods/{mod_name}", targets=[fdata_path])

        a_f.close()
        return [is_full_mod, mod_name]

    elif ".zip" in file_path:
        a_f = zipfile.ZipFile(file_path)
        content_list = a_f.namelist()

        yumiamod_json_path = None
        fdata_path = None
        for each_file_name in content_list:
            if ".yumiamod.json" in each_file_name:
                yumiamod_json_path = each_file_name
            elif ".fdata" in each_file_name:
                fdata_path = each_file_name

        if fdata_path != None:
            a_f.extract(fdata_path, f"./mods/{mod_name}")
            if yumiamod_json_path != None:
                a_f.extract(yumiamod_json_path, f"./mods/{mod_name}")
                is_full_mod = True
                
        a_f.close()
        return [is_full_mod, mod_name]
    
    return None


def call_yumia_mod_insert_into_rdb(yumia_path):
    if not os.path.exists(f"{yumia_path}/Motor/yumia_mod_insert_into_rdb.exe"):
        copy("./yumia_mod_insert_into_rdb.exe", f"{yumia_path}/Motor/yumia_mod_insert_into_rdb.exe")
    
    os.system(f"\"{yumia_path}/Motor/yumia_mod_insert_into_rdb.exe\"")

def back_up_rdb_rdx(yumia_path):
    if not os.path.exists("./backup"):
        os.mkdir("./backup")

    if os.path.exists(f"{yumia_path}/Motor/root.rdb") and os.path.exists(f"{yumia_path}/Motor/root.rdx"):
        if not os.path.exists("./backup/root.rdb"):
            copy(f"{yumia_path}/Motor/root.rdb", "./backup/root.rdb")
        if not os.path.exists("./backup/root.rdx"):
            copy(f"{yumia_path}/Motor/root.rdx", "./backup/root.rdx")

def find_fdata(mod_name) -> str|None:
    fdata_path = None
    for root, _, files in os.walk(f"./mods/{mod_name}", followlinks=False):
        for file in files:
            if ".fdata" in file:
                fdata_path = f"{root}/{file}"

    return fdata_path

def find_yumiamod_json(mod_name) -> str|None:
    yumiamod_json_path = None
    for root, _, files in os.walk(f"./mods/{mod_name}", followlinks=False):
        for file in files:
            if ".yumiamod.json" in file:
                yumiamod_json_path = f"{root}/{file}"

    return yumiamod_json_path

def insert_mod_to_Motor(yumia_path, mod_path) -> str:
    yumiamod_json_path = None
    fdata_path = None
    for root, _, files in os.walk(mod_path, followlinks=False):
        for file in files:
            if ".yumiamod.json" in file:
                yumiamod_json_path = f"{root}/{file}"
            elif ".fdata" in file:
                fdata_path = f"{root}/{file}"

    if yumiamod_json_path != None and fdata_path != None:
        copy(yumiamod_json_path, f"{yumia_path}/Motor/{os.path.basename(yumiamod_json_path)}")
        copy(fdata_path, f"{yumia_path}/Motor/{os.path.basename(fdata_path)}")
    else:
        print(f"mod file error\nfdata: {fdata_path}\njson:{yumiamod_json_path}")
            
    return os.path.basename(yumiamod_json_path)

def dump_rdb_rdx(yumia_path, json_list):
    call_yumia_mod_insert_into_rdb(yumia_path)
    for i in json_list:
        if os.path.exists(f"{yumia_path}/Motor/{i}"):
            os.remove(f"{yumia_path}/Motor/{i}")

def restore_rdb_rdx(yumia_path):
    if os.path.exists("./backup/root.rdb") and os.path.exists("./backup/root.rdx"):
        copy("./backup/root.rdb", f"{yumia_path}/Motor/root.rdb")
        copy("./backup/root.rdx", f"{yumia_path}/Motor/root.rdx")

def get_conflict_mods(target_mod_name) -> list[str]:
    conflict_mods_list = []

    fdata_name = None
    for _, _, files in os.walk(f"./mods/{target_mod_name}", followlinks=False):
        for file in files:
            if ".fdata" in file:
                fdata_name = f"{file}"
                break
            if fdata_name != None:
                break

    mods_name = os.listdir("./mods")
    for mod_name in mods_name:
        if mod_name == target_mod_name:
            continue
        for _, _, files in os.walk(f"./mods/{mod_name}", followlinks=False):
            for file in files:
                if file == fdata_name:
                    conflict_mods_list.append(mod_name)

    return conflict_mods_list

def enable_mod(yumia_path, target_mod_name):
    restore_rdb_rdx(yumia_path)
    json_list = []
    json_list.append(insert_mod_to_Motor(yumia_path, f"./mods/{target_mod_name}"))
    #insert_mod_to_Motor(yumia_path, f"./mods/{target_mod_name}")

    dump_rdb_rdx(yumia_path, json_list)
    f = open(f"./mods/{target_mod_name}/.enable", "w")
    f.close()

def disable_mod(yumia_path, target_mod_name):
    enable_mods_list = get_enable_mods_list()

    target_mod_file = None
    for _, _, files in os.walk(f"./mods/{target_mod_name}", followlinks=False):
        for file in files:
            if ".fdata" in file:
                target_mod_file = file
                break
            if target_mod_file != None:
                break

    if os.path.exists(f"{yumia_path}/Motor/{file}"):
        os.remove(f"{yumia_path}/Motor/{file}")

    restore_rdb_rdx(yumia_path)
    json_list = []
    for mod in enable_mods_list:
        if mod == target_mod_name:
            continue
        json_list.append(insert_mod_to_Motor(yumia_path, f"./mods/{mod}"))
    
    dump_rdb_rdx(yumia_path, json_list)

    if os.path.exists(f"./mods/{target_mod_name}/.enable"):
        os.remove(f"./mods/{target_mod_name}/.enable")


def get_enable_mods_list() -> list[str]:
    enable_mods_list = []
    mods_name = os.listdir("./mods")
    for mod_name in mods_name:
        if os.path.exists(f"./mods/{mod_name}/.enable"):
            enable_mods_list.append(mod_name)

    return enable_mods_list

def get_all_mods_list() -> list[str]:
    return os.listdir("./mods")

def check_mod_state(target_mod_name) -> bool:
    if os.path.exists(f"./mods/{target_mod_name}/.enable"):
        return True
    return False
    

if __name__ == "__main__":
    pass























