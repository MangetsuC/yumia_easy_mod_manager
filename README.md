# Yumia Easy Mod Manager

This is a extremly easy mod manager for the game Atelier Yumia based on the [wonderful work](https://github.com/eArmada8/yumia_fdata_tools) from [@eArmada8](https://github.com/eArmada8). The manager has basic functions to manager your mods, like import mod file, enable or disable. 

## Usage

![yumia easy mod manager gui](https://s2.loli.net/2025/03/28/5mqfKvd1Ewb8ZeR.png)

Your mods are listed in the first column, other mods which have conflict are listed in the second column. With the button in the third column, you could manager your mods easily.

## Initial launch

The mod manager will donwload the very important toll yumia_mod_insert_into_rdb.exe from [@eArmada8](https://github.com/eArmada8) first. Then it will ask you select the game main file Atelier_Yumia.exe.

## What is mods conflict

Now, the mod for the game Atelier Yumia needs unique 8-digit hexadecimal code. Thus, the mods have same 8-digit hexadecimal code are incompatible. Just edit the hex code by yourself in the right text box and click Reset hash button.

## Mod file requirements

Your mod should has single fdata file. The mod manager could import 7z file or zip file or fdata file. If there is yumiamod.json file in the archive file, the mod manager will use it first instead of generating yumiamod.json file based on fdata file.


