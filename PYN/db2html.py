import os
import sqlite3

# SQLiteデータベースに接続
conn = sqlite3.connect('./settings.db')
cursor = conn.cursor()

# ディレクトリを生成する関数
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# HTMLヘッダーの作成
def generate_html_header(title):
    return f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 20px;
            }}
            h2 {{
                text-align: center;
                color: #333;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 18px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #009879;
                color: white;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            td {{
                background-color: #ffffff;
            }}
            tr:nth-child(even) {{
                background-color: #f8f8f8;
            }}
        </style>
    </head>
    <body>
    """

# データベースから必要なデータを抽出
cursor.execute("SELECT id, Model, Coeff, Nuclide, Intensity, Symbol, A, Z, N, F0Be, F1t, F1a, F5Mat, F5t, F5a, "
               "D1_Brho, D2_Brho, D3_Brho, D4_Brho, D5_Brho, D6_Brho, D7_Brho, D8_Brho, "
               "D1_Energy, D2_Energy, D3_Energy, D4_Energy, D5_Energy, D6_Energy, D7_Energy, D8_Energy, "
               "DumpL, DumpR, F1L, F1R, F2L, F2R, F25XL, F25XR, F25YL, F25YR, F5L, F5R, F7L, F7R FROM Settings")
settings_data = cursor.fetchall()

# モダンなHTMLテーブルのヘッダー
html_content = generate_html_header("Settings Data")
html_content += """
<h2>TRIP-S3CAN 2024 Autumn | LISE++ settings configuration</h2>
<p style="text-align: center;">
    <a href="https://docs.google.com/spreadsheets/d/1M_SNlWawUvMURzTSM3Ee6sIytSjhj-jcXCrngcpWuiU/edit?usp=sharing" target="_blank">Google Sheets</a>
</p>
<table>
<tr>
  <th>id</th><th>LPP</th><th>JSROOT</th><th>Model</th><th>Coeff</th><th>Nuclide</th><th>Intensity</th><th>Symbol</th><th>A</th><th>Z</th><th>N</th>
  <th>F0Be</th><th>F1t</th><th>F1a</th><th>F5Mat</th><th>F5t</th><th>F5a</th>
  <th>D1_Brho</th><th>D2_Brho</th><th>D3_Brho</th><th>D4_Brho</th><th>D5_Brho</th><th>D6_Brho</th><th>D7_Brho</th><th>D8_Brho</th>
  <th>D1_Energy</th><th>D2_Energy</th><th>D3_Energy</th><th>D4_Energy</th><th>D5_Energy</th><th>D6_Energy</th><th>D7_Energy</th><th>D8_Energy</th>
  <th>DumpL</th><th>DumpR</th><th>F1L</th><th>F1R</th><th>F2L</th><th>F2R</th><th>F25XL</th><th>F25XR</th><th>F25YL</th><th>F25YR</th>
  <th>F5L</th><th>F5R</th><th>F7L</th><th>F7R</th>
</tr>
"""

# 個別のid.htmlファイルを生成するためのループ
for row in settings_data:
    id_value = row[0]
    symbol_value = row[5]

    # ファイルパスを生成
    file_path = f"BigRIPS_NoXX_136Xe_{symbol_value}/{id_value}.lpp"
    js_path = f"http://localhost/CGI-BIN/JSROOT/TRIP/S3CAN/2024/AUTUMN/LISE/temp.pl?id={id_value}&symbol={symbol_value}"

    # HTML行を追加 (個別のhtmlファイルへのリンクを追加)
    html_content += f"<tr><td><a href='BigRIPS_NoXX_136Xe_{symbol_value}/{id_value}.html'>{id_value}</a></td><td>{file_path}</td><td><a href='{js_path}'>URL</a></td>"

    # 各セルの内容をチェックし、数値なら小数点以下2桁にフォーマット
    for i, cell in enumerate(row[1:]):
        # Brho (D1_Brho から D8_Brho) に対応する列は 16〜23番目
        if i in range(14, 22) and isinstance(cell, (int, float)):
            html_content += f"<td>{cell:.4f}</td>"  # Brho 値は小数点以下4桁
        elif i in range(5, 8) and isinstance(cell, (int, float)):
            html_content += f"<td>{cell:.0f}</td>"  # Brho 値は小数点以下4桁
        elif i in range(22, 30) and isinstance(cell, (int, float)):
            html_content += f"<td>{cell:.0f}</td>"  # Brho 値は小数点以下4桁
        elif isinstance(cell, (int, float)):  # その他の数値は小数点以下2桁
            html_content += f"<td>{cell:.2f}</td>"
        else:  # 数値でない場合はそのまま表示
            html_content += f"<td>{cell}</td>"

    html_content += "</tr>\n"

    # 個別のディレクトリを作成
    dir_path = f"./HTML/BigRIPS_NoXX_136Xe_{symbol_value}"
    create_directory(dir_path)

    # Isotopeテーブルから該当するsetting_idのデータを取得
    cursor.execute("SELECT id, isotope_name, A, Z, N, Yield, percent1, x_section, "
                   "Transmission, Transmission_F1slit, Transmission_F2slit, "
                   "Transmission_F25slit, Transmission_F5slit, Transmission_F7slit, "
                   "Qratio_F3, Qratio_F5, Unreacted_F5 "
                   "FROM Isotopes WHERE setting_id = ?", (id_value,))
    isotope_data = cursor.fetchall()

    # 個別のhtmlファイルの内容を作成
    isotope_html_content = generate_html_header(f"Isotope Data for Setting ID {id_value}")
    isotope_html_content += f"""
    <h2>Isotope Data for Setting ID {id_value} ({symbol_value})</h2>
    <table>
    <tr>
      <th>id</th><th>Isotope Name</th><th>A</th><th>Z</th><th>N</th><th>Yield</th><th>percent1</th><th>x_section</th>
      <th>Transmission</th><th>Transmission_F1slit</th><th>Transmission_F2slit</th>
      <th>Transmission_F25slit</th><th>Transmission_F5slit</th><th>Transmission_F7slit</th>
      <th>Qratio_F3</th><th>Qratio_F5</th><th>Unreacted_F5</th>
    </tr>
    """

    # isotope_dataをidでソート
    isotope_data.sort(key=lambda x: x[0])  # x[0] は id に対応

    # 各Isotope行をHTMLに変換して追加
    for isotope_row in isotope_data:
        isotope_html_content += "<tr>"
        for i, cell in enumerate(isotope_row):
            # Yield、percent1、x_section は小数点以下2桁
            if i in [5, 6]:  # 6がpercent1、7がx_section
                isotope_html_content += f"<td>{cell:.2f}</td>" if isinstance(cell, (int, float)) else f"<td>{cell}</td>"
            # Transmission系は小数点以下4桁
            elif i == 7:
                isotope_html_content += f"<td>{cell:.2e}</td>" if isinstance(cell, (int, float)) else f"<td>{cell}</td>"
            elif i in range(8, 14):  # Transmission系
                isotope_html_content += f"<td>{cell:.4f}</td>" if isinstance(cell, (int, float)) else f"<td>{cell}</td>"
            elif i in range(14, 17):  # Transmission系
                isotope_html_content += f"<td>{cell*100:.2f}</td>" if isinstance(cell, (int, float)) else f"<td>{cell}</td>"
            # それ以外の列はそのまま
            else:  
                isotope_html_content += f"<td>{cell}</td>"
    
    isotope_html_content += "</tr>\n"

    # HTMLのフッターを追加
    isotope_html_content += """
    </table>
    </body>
    </html>
    """

    # 各idに対応するHTMLファイルを保存
    with open(f"{dir_path}/{id_value}.html", "w") as file:
        file.write(isotope_html_content)

# HTMLのフッターを追加
html_content += """
</table>
</body>
</html>
"""

# index.htmlファイルに書き込み
with open("./HTML/index.html", "w") as file:
    file.write(html_content)

# データベースを閉じる
conn.close()

print("index.htmlと各idごとのHTMLファイルが生成されました。")

