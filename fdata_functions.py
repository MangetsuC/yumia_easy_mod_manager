#This file is written based on the github.com/eArmada8/yumia_fdata_tools/yumia_mod_find_metadata.py
#This file is used to generate yumiamod.json file based on single moded fdata file and origin root.rdb file

import struct, base64, json

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

def generate_yumiamod_json(target_hash, target_fdata, origin_rdb) -> bool:
    target_hash = str(target_hash)
    if len(target_hash) != 8:
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
    
    with open(f'0x{target_hash}.yumiamod.json', 'wb') as f:
        f.write(json.dumps(dict(fdata_hash = int(target_hash, 16), files = files_metadata), indent = 4).encode())

    return True

if __name__ == "__main__":
    pass






