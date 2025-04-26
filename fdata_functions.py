#This file is written based on the github.com/eArmada8/yumia_fdata_tools
#This file is used to generate yumiamod.json file based on single moded fdata file and origin root.rdb file
#check_rdb_rdx_reset read root.rdb and root.rdx file to check whether they are updated

import struct, base64, json, pathlib
import os, shutil

def find_file_metadata_in_rdb (target_filehash, rdb_file = 'root.rdb'):
    r_metadata = b''
    with open(rdb_file, 'rb') as f:
        f.seek(0,2)
        eof = f.tell()
        f.seek(0x20,0)
        while f.tell() < eof:
            start = f.tell()
            magic = f.read(4)
            assert magic == b'IDRK'
            _, entry_size, string_size, _ = struct.unpack("<I3Q", f.read(28))
            _, file_hash, tkid, _ = struct.unpack("<4I", f.read(16))
            if not file_hash == target_filehash:
                f.seek(start + entry_size + 4 - (entry_size % 4))
            else:
                r_metadata = f.read(entry_size - 0x3D)
                footer = struct.unpack("<H2IHI", f.read(16))
                break
    return(tkid, string_size, footer, r_metadata)

def find_all_file_metadata_in_fdata(fdata_file):
    target_list = []
    this_offset = 0
    with open(fdata_file, 'rb') as f:
        while True:
            b_data = f.read(2048)
            if b_data == b'':
                break
            b_index = b_data.find(b'IDRK0000')
            if b_index != -1:
                this_offset += b_index
                f.seek(this_offset)
                magic = f.read(8)
                assert magic == b'IDRK0000'
                entry_size, cmp_size, _ = struct.unpack("<3Q", f.read(24))
                _, filehash, _, _ = struct.unpack("<4I", f.read(16))
                f_metadata = f.read(entry_size - cmp_size - 0x30)
                target_list.append(dict(name_hash = filehash, f_metadata = f_metadata))

            this_offset = f.tell()
    return target_list

def generate_yumiamod_json(target_hash, target_fdata, origin_rdb, target_path) -> bool:
    target_hash = str(target_hash)
    if len(target_hash) != 8:
        print(f"unkown fdata hash: {target_hash}")
        return False
    all_file_list = find_all_file_metadata_in_fdata(target_fdata)
    files_metadata = []
    for file in all_file_list:
        name_hash = file['name_hash']
        f_metadata = file['f_metadata']

        tkid, string_size, _, r_metadata = find_file_metadata_in_rdb(name_hash, rdb_file = origin_rdb)

        metadata = {'name_hash': name_hash, 'tkid_hash': tkid, 'string_size': string_size,\
            'f_extradata': base64.b64encode(f_metadata).decode(),\
            'r_extradata': base64.b64encode(r_metadata).decode()}
        files_metadata.append(metadata)
    
    with open(f'{target_path}/0x{target_hash}.yumiamod.json', 'wb') as f:
        f.write(json.dumps(dict(fdata_hash = int(target_hash, 16), files = files_metadata), indent = 4).encode())

    return True

def read_decode_mod_json(mod_json_filename):
    mod_data = json.loads(open(mod_json_filename, 'rb').read())
    for i in range(len(mod_data['files'])):
        mod_data['files'][i]['f_extradata'] = base64.b64decode(mod_data['files'][i]['f_extradata'])
        mod_data['files'][i]['r_extradata'] = base64.b64decode(mod_data['files'][i]['r_extradata'])
    return(mod_data)

def append_rdx(new_fdata_list, rdx_file = 'root.rdx'):
    with open(rdx_file, 'rb') as f:
        new_rdx = f.read()
        eof = f.tell()
        f.seek(0)
        while f.tell() < eof:
            marker, ff, fdata = struct.unpack("<2hI", f.read(8))
        markers = []
        for new_fdata in new_fdata_list:
            marker += 1
            packed_data = struct.pack("<2hI", marker, -1, new_fdata)
            new_rdx += packed_data
            markers.append(marker)
        return(markers)
    
def create_rdb_idrk(filesize, file_metadata, fdata_index = 0, fdata_offset = 0x10):
    extrasize = len(file_metadata['r_extradata'])
    idrk = bytearray()
    idrk.extend(b'IDRK0000')
    idrk.extend(struct.pack("<3Q", 0x3D + extrasize, file_metadata['string_size'], filesize))
    idrk.extend(struct.pack("<4I", 0, file_metadata['name_hash'], file_metadata['tkid_hash'], 0x20000))
    idrk.extend(file_metadata['r_extradata'])
    idrk.extend(struct.pack("<H2IHI", 0x401, fdata_offset, 0x30 + extrasize + filesize, fdata_index, 0))
    return(idrk)

def read_fdata_for_rdb_insertion(mod_data, fdata_file_path, fdata_index):
    with open(fdata_file_path, 'rb') as f:
        f.seek(0,2)
        eof = f.tell()
        f.seek(0x10,0) # Skip header
        idrk_struct = {}
        while f.tell() < eof:
            fdata_offset = f.tell()
            magic = f.read(8)
            if not magic == b'IDRK0000':
                while f.tell() < eof and not magic == b'IDRK0000':
                    if f.tell() >= eof:
                        break
                    f.seek(-4,1)
                    fdata_offset = f.tell()
                    magic = f.read(8)
            entry_size, _, unc_size = struct.unpack("<3Q", f.read(24))
            _, name_hash, _, _ = struct.unpack("<4I", f.read(16))
            if name_hash in [x['name_hash'] for x in mod_data['files']]:
                metadata = [x for x in mod_data['files'] if x['name_hash'] == name_hash][0]
                idrk_struct[name_hash] = create_rdb_idrk(unc_size, metadata,\
                    fdata_index = fdata_index, fdata_offset = fdata_offset)
            f.seek(fdata_offset + entry_size)
        return (idrk_struct)

def check_rdb_rdx_reset(mods_path:str, motor_path:str) -> bool:
    yumiamod_jsons: list[str] = []
    for root, _, files in os.walk(mods_path, followlinks=False):
        for file in files:
                if ".yumiamod.json" in file:
                    yumiamod_jsons.append(f"{root}/{file}")

    fdata_files = []
    for yumiamod_json in yumiamod_jsons:
        json_path = pathlib.Path(yumiamod_json.replace(mods_path, ""))
        hex_code = json_path.name.replace(".yumiamod.json", "")
        json_parent_dir = mods_path + list(json_path.parts)[0] + list(json_path.parts)[1]
        for root, _, files in os.walk(json_parent_dir, followlinks=False):
            for file in files:
                    if ".fdata" in file:
                        if file.replace(".fdata", "") == hex_code:
                            fdata_files.append(f"{root}/{file}")

    mod_datas = [read_decode_mod_json(x) for x in yumiamod_jsons]

    mod_fdata_hashes = [x["fdata_hash"] for x in mod_datas]

    with open(f'{motor_path}/root.rdx', 'rb') as f:
        f.seek(0, 2)
        eof = f.tell()
        f.seek(0)
        appearance_markers: list[int, list[int]] = []
        while f.tell() < eof:
            marker, _, fdata = struct.unpack("<2hI", f.read(8))

            match_index = []
            for fdata_i in range(len(mod_fdata_hashes)):
                if fdata == mod_fdata_hashes[fdata_i]:
                    match_index.append(fdata_i)

            if match_index != []:
                appearance_markers.append([marker, match_index])

    possible_idrk_structs = []
    possible_mods_checksum = []
    for possible_mod_marker in appearance_markers:
        marker = possible_mod_marker[0]
        possible_mods_index = possible_mod_marker[1]
        tmp_idrk_structs = []
        tmp_mods_checksum = []
        for mod_index in possible_mods_index:
            this_idrk_struct = read_fdata_for_rdb_insertion(mod_datas[mod_index], fdata_files[mod_index], marker)
            tmp_mods_checksum.append(len(this_idrk_struct))
            tmp_idrk_structs.append(this_idrk_struct)
        
        possible_idrk_structs.append(tmp_idrk_structs)
        possible_mods_checksum.append(tmp_mods_checksum)

    possible_name_hashes = []

    for i in possible_idrk_structs:
        for j in i:
            for k in j.keys():
                possible_name_hashes.append(list(struct.unpack("<I", j[k][36:40]))[0])

    possible_name_hashes = list(set(possible_name_hashes))

    with open(f'{motor_path}/root.rdb', 'rb') as f:
        f.seek(0,2)
        eof = f.tell()
        f.seek(32,0)
        while f.tell() < eof:
            start = f.tell()
            magic = f.read(4)
            if magic == b'IDRK':
                _, entry_size, _, _ = struct.unpack("<I3Q", f.read(28))
                _, file_hash, _, _ = struct.unpack("<4I", f.read(16))

                if file_hash in possible_name_hashes:
                    f.seek(start)
                    in_file_idrk_struct = f.read(entry_size + 4 - (entry_size % 4))

                    for i in range(len(possible_idrk_structs)):
                        for j in range(len(possible_idrk_structs[i])):
                            this_idrk_structs = possible_idrk_structs[i][j]
                            for k in this_idrk_structs.keys():
                                if in_file_idrk_struct == this_idrk_structs[k]:
                                    possible_mods_checksum[i][j] -= 1
                                    break

    for i in range(len(possible_mods_checksum)):
        for j in range(len(possible_mods_checksum[i])):
            #mod_json_name = yumiamod_jsons[appearance_markers[i][1][j]]
            if possible_mods_checksum[i][j] <= 0:
                return False
            
    print("There is no mod data in root.rdb and root.rdx. The game may be updated. New root.rdb and root.rdx are backup.")
    return True


if __name__ == "__main__":
    pass






