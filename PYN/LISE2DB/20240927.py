import re
import math

# 汎用的な変数抽出関数
def extract_variable(content, start_pattern, value_pattern, group_indices, var_names):
    in_block = False
    extracted_values = {}

    for line in content:
        # ブロックの開始を確認
        if re.search(start_pattern, line):
            in_block = True
            continue
        
        # ブロック内の変数抽出
        if in_block:
            match = re.search(value_pattern, line)
            if match:
                for i, var_name in enumerate(var_names):
                    extracted_values[var_name] = match.group(group_indices[i])
                break  # 変数が見つかったら終了

    return extracted_values

# ファイルの内容を読み込む関数
def extract_data_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()

    # 結果を格納する辞書
    extracted_data = {}

    # 各種変数を抽出
    # ===== Settings ================================================================================
    # === Mechanism of PF ===
    extracted_data["Model"] = extract_variable(
        content, 
        r"\[convolution\]",                  # ブロックの開始パターン
        r"Convolution mode = ([+-]?[\d.]+)", # 値のパターン
        [1],                                 # 抽出したいグループのインデックス（数字とシンボル）
        ["Model"]            # 対応する変数名
    )

    extracted_data["Coeff"] = extract_variable(
        content, 
        r"\[convolution\]",                  # ブロックの開始パターン
        r"CoefConv_1 = ([+-]?[\d.]+)",       # 値のパターン
        [1],                                 # 抽出したいグループのインデックス（数字とシンボル）
        ["Coeff"]            # 対応する変数名
    )

    # === Primary Beam ===
    extracted_data["Primary Beam"] = extract_variable(
        content, 
        r"\[settings\]",              # ブロックの開始パターン
        r"A,Z,Q = (\d+)([A-Za-z]+)",  # 値のパターン
        [1, 2],                          # 抽出したいグループのインデックス（数字とシンボル）
        ["Mass", "Symbol"]            # 対応する変数名
    )

    # === Intensity ===
    extracted_data["Intensity"] = extract_variable(
        content, 
        r"\[settings\]",              # ブロックの開始パターン
        r"Intensity = ([\d.]+)",  # 値のパターン
        [1],                          # 抽出したいグループのインデックス（数字とシンボル）
        ["Intensity"]            # 対応する変数名
    )

    # === Centered Nuclide ===
    extracted_data["Centered Nuclide"] = extract_variable(
        content, 
        r"\[settings\]",              # ブロックの開始パターン
        r"Settings on A,Z = (\d+)([A-Za-z]+)",  # 値のパターン
        [1, 2],                          # 抽出したいグループのインデックス（数字とシンボル）
        ["Mass", "Symbol"]            # 対応する変数名
    )

    # ===== Beam-line materials =====================================================================
    # === F0 Be ===
    # = Atomic Number and Mass
    extracted_data["Target_Z_Mass"] = extract_variable(
        content, 
        r"\[target\]",              # ブロックの開始パターン
        r"Target contents = ([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+)",  # 値のパターン
        [2, 4],                          # 抽出したいグループのインデックス
        ["Z", "Mass"]                    # 対応する変数名
    )

    # = Thickness
    extracted_data["Target_thickness"] = extract_variable(
        content, 
        r"\[target\]", 
        r"Target thickness = ([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+)", 
        [2], 
        ["thickness"]
    )

    # === F1/5 deg ===
    for wedge in ["F1", "F5"]:
        # = Atomic Number and Mass
        extracted_data[f"{wedge}_Wedge_Z_Mass"] = extract_variable(
            content, 
            rf"Name = {wedge} Wedge", 
            r"contents1 = ([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+)", 
            [2, 4], 
            ["Z", "Mass"]
        )

        # = Thickness
        extracted_data[f"{wedge}_Wedge_thickness"] = extract_variable(
            content, 
            rf"Name = {wedge} Wedge", 
            r"thickness = ([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+)", 
            [2], 
            ["Thickness"]
        )

        # = Angle
        extracted_data[f"{wedge}_Wedge_Angle"] = extract_variable(
            content, 
            rf"Name = {wedge} Wedge", 
            r"Angle = ([+-]?[\d.]+)", 
            [1], 
            ["Angle"]
        )

    # ===== Brho (Tm) ===============================================================================
    for i in range(1, 9):
        extracted_data[f"D{i}_Brho"] = extract_variable(
            content, 
            rf"\[D{i}_DipoleSettings\]", 
            r"Brho = ([+-]?[\d.]+)\s+Tm", 
            [1], 
            ["Brho"]
        )

    # ===== Slit (mm) ===============================================================================
    # === Beamdump ===
    extracted_data["ExitBeamDump_x_width"] = extract_variable(
        content, 
        r"Name = ExitBeamDump", 
        r"X_size = ([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+)", 
        [2, 4], 
        ["Left", "Right"]
    )

    # === Focal Planes (X) ===
    for slit in ["F1", "F2", "F2.5", "F5", "F7"]:
        extracted_data[f"{slit}_slit_x_width"] = extract_variable(
            content, 
            rf"Name = {slit} slit", 
            r"X_size = ([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+)", 
            [2, 4], 
            ["Left", "Right"]
        )

    # === Focal Planes (Y) ===
    for slit in ["F2.5"]:
        extracted_data[f"{slit}_slit_y_width"] = extract_variable(
            content, 
            rf"Name = {slit} slit", 
            r"Y_size = ([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+),([+-]?[\d.]+)", 
            [2, 4], 
            ["Left", "Right"]
        )

    return extracted_data

# ファイルパスを指定
file_path = "BigRIPS_NoXX_136Xe_XXX.lpp"

# 抽出結果を取得
data = extract_data_from_file(file_path)

# 原子番号を元素記号から取得する辞書
element_dict = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6,
    "N": 7, "O": 8, "F": 9, "Ne": 10, "Na": 11, "Mg": 12,
    "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18,
    "K": 19, "Ca": 20, "Sc": 21, "Ti": 22, "V": 23, "Cr": 24,
    "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30,
    "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36,
    "Rb": 37, "Sr": 38, "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42,
    "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48,
    "In": 49, "Sn": 50, "Sb": 51, "Te": 52, "I": 53, "Xe": 54,
    "Cs": 55, "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60,
    "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64, "Tb": 65, "Dy": 66,
    "Ho": 67, "Er": 68, "Tm": 69, "Yb": 70, "Lu": 71, "Hf": 72,
    "Ta": 73, "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78,
    "Au": 79, "Hg": 80, "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84,
    "At": 85, "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90,
    "Pa": 91, "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96,
    "Bk": 97, "Cf": 98, "Es": 99, "Fm": 100, "Md": 101, "No": 102,
    "Lr": 103, "Rf": 104, "Db": 105, "Sg": 106, "Bh": 107, "Hs": 108,
    "Mt": 109, "Ds": 110, "Rg": 111, "Cn": 112, "Nh": 113, "Fl": 114,
    "Mc": 115, "Lv": 116, "Ts": 117, "Og": 118
}

# Mechanism of PF
Model = data["Model"]["Model"]
Coeff = data["Coeff"]["Coeff"]

# Primary Beam
Nuclide   = data["Primary Beam"]["Mass"] + data["Primary Beam"]["Symbol"]
Intensity = data["Intensity"]["Intensity"]

# Nuclide on central orbit
Symbol = data["Centered Nuclide"]["Mass"] + data["Centered Nuclide"]["Symbol"]
A      = float(data["Centered Nuclide"]["Mass"]  )         
symbol = data["Centered Nuclide"]["Symbol"]
Z      = float(element_dict.get(symbol, None)    )      
N      = A - Z      

# Beam-line materials
F0Be  = data["Target_thickness"]  ["thickness"]
F1t   = data["F1_Wedge_thickness"]["Thickness"]
F1a   = data["F1_Wedge_Angle"]    ["Angle"]
F5Mat = "C"
F5t   = data["F5_Wedge_thickness"]["Thickness"]
F5a   = data["F5_Wedge_Angle"]    ["Angle"]

# エネルギーを計算する関数
def calculate_energy(Mass, Z, Brho):
    # 931.494 MeV/c² からエネルギーを計算
    energy = 931.494 * (math.sqrt(1 + (299.8 * Z * Brho / (Mass * 931.494))**2) - 1)
    return energy

# settingsを定義
settings = {}

# 変数をsettingsに詰め込む
settings["Model"] = Model
settings["Coeff"] = Coeff
settings["Nuclide"] = Nuclide
settings["Intensity"] = Intensity
settings["Symbol"] = Symbol
settings["A"] = A
settings["Z"] = Z
settings["N"] = N
settings["F0Be"] = F0Be
settings["F1t"] = F1t
settings["F1a"] = F1a
settings["F5Mat"] = F5Mat
settings["F5t"] = F5t
settings["F5a"] = F5a

# D1からD8までのBrhoをsettingsに追加
for i in range(1, 9):
    brho_key = f"D{i}_Brho"
    settings[brho_key] = float(data[brho_key]["Brho"])

# エネルギー計算を行い、結果をsettingsに追加
for i in range(1, 9):
    brho_value = settings[f"D{i}_Brho"]
    energy = calculate_energy(A, Z, brho_value)  # 例としてAとZを使用
    settings[f"D{i}_Energy"] = energy

settings["DumpL"]  = data["ExitBeamDump_x_width"]["Left"]
settings["DumpR"]  = data["ExitBeamDump_x_width"]["Right"]
settings["F1L"]    = data["F1_slit_x_width"]     ["Left"]
settings["F1R"]    = data["F1_slit_x_width"]     ["Right"]
settings["F2L"]    = data["F2_slit_x_width"]     ["Left"]
settings["F2R"]    = data["F2_slit_x_width"]     ["Right"]
settings["F2.5XL"] = data["F2.5_slit_x_width"]   ["Left"]
settings["F2.5XR"] = data["F2.5_slit_x_width"]   ["Right"]
settings["F2.5YL"] = data["F2.5_slit_y_width"]   ["Left"]
settings["F2.5YR"] = data["F2.5_slit_y_width"]   ["Right"]
settings["F5L"]    = data["F5_slit_x_width"]     ["Left"]
settings["F5R"]    = data["F5_slit_x_width"]     ["Right"]
settings["F7L"]    = data["F7_slit_x_width"]     ["Left"]
settings["F7R"]    = data["F7_slit_x_width"]     ["Right"]

# 結果を表示
print(settings)

