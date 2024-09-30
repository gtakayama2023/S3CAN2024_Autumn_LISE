import sqlite3
from datetime import datetime
import ROOT
from ROOT import TCanvas, TLatex, TH2F, TFile

# バッチモードを有効にする
ROOT.gROOT.SetBatch(True)

# データベースから同位体データと設定を取得
def fetch_isotope_data_and_symbols(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Isotope と Settings を結合してデータを取得
    query = """
    SELECT 
        I.setting_id, 
        I.Z, 
        I.N, 
        I.isotope_name, 
        I.Yield, 
        I.percent1,
        I.x_section,
        I.Transmission,
        I.Transmission_F1slit,
        I.Transmission_F2slit,
        I.Transmission_F25slit,
        I.Transmission_F5slit,
        I.Transmission_F7slit,
        S.Symbol 
    FROM 
        Isotopes I 
    JOIN 
        Settings S 
    ON 
        I.setting_id = S.id
    """
    cursor.execute(query)

    isotopes_by_setting_id = {}
    for row in cursor.fetchall():
        (setting_id, Z, N, isotope_name, yield_value, percent1, x_section, Transmission, 
         Transmission_F1slit, Transmission_F2slit, Transmission_F25slit, 
         Transmission_F5slit, Transmission_F7slit, symbol) = row
        
        if setting_id not in isotopes_by_setting_id:
            isotopes_by_setting_id[setting_id] = {'isotopes': [], 'symbol': symbol}
        isotopes_by_setting_id[setting_id]['isotopes'].append(
            (Z, N, isotope_name, yield_value, percent1, x_section, Transmission, 
             Transmission_F1slit, Transmission_F2slit, Transmission_F25slit, 
             Transmission_F5slit, Transmission_F7slit)
        )

    conn.close()
    return isotopes_by_setting_id

# 同位体データと設定を取得
isotopes_by_setting_id = fetch_isotope_data_and_symbols("./settings.db")

# ヒストグラムを作成する範囲
Nmin, Nmax = 40, 84  # 中性子数の範囲
Zmin, Zmax = 35, 56  # 陽子数の範囲

# 描画するパラメータのリスト
parameters = [
    ("Yield", "cYield"),
    ("percent1", "cpercent1"),
    ("x_section", "c_x_section"),
    ("Transmission", "cTransmission"),
    ("Transmission_F1slit", "cTransmission_F1slit"),
    ("Transmission_F2slit", "cTransmission_F2slit"),
    ("Transmission_F25slit", "cTransmission_F25slit"),
    ("Transmission_F5slit", "cTransmission_F5slit"),
    ("Transmission_F7slit", "cTransmission_F7slit")
]

# 各 setting_id に対して個別にROOTファイルを作成
for setting_id, data in isotopes_by_setting_id.items():
    isotopes = data['isotopes']
    symbol = data['symbol']

    # ROOTファイルのパス
    root_file_path = f"./ROOT/BigRIPS_NoXX_136Xe_{symbol}/{setting_id}.root"
    
    # ディレクトリの作成（存在しない場合）
    import os
    os.makedirs(os.path.dirname(root_file_path), exist_ok=True)

    # ROOTファイルを作成
    root_file = TFile(root_file_path, "RECREATE")

    # 各パラメータに対応するキャンバスとヒストグラムを生成
    for param_name, canvas_prefix in parameters:
        if param_name == 'percent1':
            continue

        # キャンバスの名前を動的に作成
        canvas_name = f"{canvas_prefix}"

        c1 = TCanvas(canvas_name, f"Nuclear Chart ({param_name}) ({symbol} ID: {setting_id})", 1000, 800)
        c1.SetLogz(1)
        c1.SetRightMargin(0.15)  # カラーバーのためにマージンを調整

        # 2次元ヒストグラムを作成してプロットの基礎とする
        h2 = TH2F(f"h2_{param_name}_{setting_id}", f"Nuclear Chart ({param_name}) ({symbol} ID: {setting_id});Neutron Number (N);Proton Number (Z)", 
                  Nmax-Nmin+1, Nmin-0.5, Nmax+0.5, Zmax-Zmin+1, Zmin-0.5, Zmax+0.5)

        # パラメータ名に対応するインデックスを設定
        param_index_map = {
            "Yield": 3,
            "percent1": 4,
            "x_section": 5,
            "Transmission": 6,
            "Transmission_F1slit": 7,
            "Transmission_F2slit": 8,
            "Transmission_F25slit": 9,
            "Transmission_F5slit": 10,
            "Transmission_F7slit": 11,
        }

        # テキストオブジェクトを保持するリスト
        text_objects = []
        text_obj2 = []

        # 各核種のパラメータ値をヒストグラムに設定
        for isotope in isotopes:
            Z, N, isotope_name, yield_value, percent1, x_section, Transmission, Transmission_F1slit, Transmission_F2slit, Transmission_F25slit, Transmission_F5slit, Transmission_F7slit = isotope
            
            # param_nameに対応するインデックスを取得
            param_value = isotope[param_index_map[param_name]]
            ratio_value = isotope[param_index_map['percent1']]
            
            if Nmin <= N <= Nmax and Zmin <= Z <= Zmax:
                h2.SetBinContent(N-Nmin+1, Z-Zmin+1, param_value)

                # 同位体名のテキストを描画
                latex = TLatex(N, Z + 0.3, isotope_name)
                latex.SetTextSize(0.02)
                latex.SetTextColor(ROOT.kGray+3)
                latex.SetTextAlign(22)  # 中央揃え
                latex.Draw()
                text_objects.append(latex)

                # 同位体の param_value を isotope_name の下に表示
                if param_name == 'Yield': 
                    param_value_text = TLatex(N, Z - 0.0, f"{param_value:.0f}")  # param_valueを表示
                elif param_name == 'x_section':
                    param_value_text = TLatex(N, Z - 0.0, f"{param_value:.0e}")  # param_valueを表示
                else:
                    param_value_text = TLatex(N, Z - 0.0, f"{param_value:.2f}")  # param_valueを表示
                param_value_text.SetTextSize(0.02)
                param_value_text.SetTextColor(ROOT.kGray+2)
                param_value_text.SetTextAlign(22)  # 中央揃え
                param_value_text.Draw()
                text_objects.append(param_value_text)

                if param_name == 'Yield':
                    # 同位体の ratio_value を isotope_name の下に表示
                    param_value_text = TLatex(N, Z - 0.3, f"{ratio_value:.1f} %")  # param_valueを表示
                    param_value_text.SetTextSize(0.02)
                    param_value_text.SetTextColor(ROOT.kGray+2)
                    param_value_text.SetTextAlign(22)  # 中央揃え
                    param_value_text.Draw()
                    text_objects.append(param_value_text)

                # グリッド線を描画
                h2.Draw("COLZ SAME")
                c1.SetGrid(1, 1)
                c1.RedrawAxis()

        h2.SetStats(1)  # 統計ボックスを表示
        
        h2.Draw("COLZ")

        # すべてのテキストオブジェクトを再描画
        for text in text_objects:
            text.Draw()

        # キャンバスをROOTファイルに保存
        c1.Write()

        # Yield に関するヒストグラムの場合、正規化を行う
        if param_name == "Yield":
            # 全 bin の合計を取得
            total_sum = h2.Integral()
            
            # 正規化を行い、新しいヒストグラムを作成
            h2_Yield_Normalized = TH2F(f"h2_Yield_Normalized_{setting_id}", 
                                        f"Yield (Normalized: {total_sum:.1f} -> 10000) ({symbol} ID: {setting_id});Neutron Number (N);Proton Number (Z)", 
                                        Nmax-Nmin+1, Nmin-0.5, Nmax+0.5, Zmax-Zmin+1, Zmin-0.5, Zmax+0.5)
            
            # 各 bin を 10000 / total_sum で正規化
            normalization_factor = 10000.0 / total_sum if total_sum > 0 else 0
            for x in range(1, h2.GetNbinsX() + 1):
                for y in range(1, h2.GetNbinsY() + 1):
                    bin_content = h2.GetBinContent(x, y)
                    h2_Yield_Normalized.SetBinContent(x, y, bin_content * normalization_factor)
                    N = x + Nmin - 1
                    Z = y + Zmin - 1

                    # NとZに基づいて同位体情報を取得
                    for isotope in isotopes:
                        isotope_Z, isotope_N, isotope_name, yield_value, percent1, x_section, Transmission, Transmission_F1slit, Transmission_F2slit, Transmission_F25slit, Transmission_F5slit, Transmission_F7slit = isotope
                        if isotope_Z == Z and isotope_N == N:
                            #print(f'isotope_Z: {isotope_Z}, Z: {Z}')
                            # 同位体名のテキストを描画
                            latex = TLatex(N, Z + 0.3, isotope_name)
                            latex.SetTextSize(0.02)
                            latex.SetTextColor(ROOT.kGray + 3)
                            latex.SetTextAlign(22)  # 中央揃え
                            latex.Draw()
                            text_obj2.append(latex)

                            # 同位体の param_value を isotope_name の下に表示
                            param_value_text = TLatex(N, Z - 0.0, f"{bin_content * normalization_factor:.0f}")  # yield_valueを表示
                            param_value_text.SetTextSize(0.02)
                            param_value_text.SetTextColor(ROOT.kGray + 2)
                            param_value_text.SetTextAlign(22)  # 中央揃え
                            param_value_text.Draw()
                            text_obj2.append(param_value_text)

            # 正規化ヒストグラムを描画
            h2_Yield_Normalized.SetStats(1)  # 統計ボックスを表示
            h2_Yield_Normalized.Draw("COLZ")

            for text in text_obj2:
                text.Draw()
            
            c1.SetGrid(1, 1)
            c1.RedrawAxis()
            c1.Write()  # 正規化ヒストグラムも保存

    # ROOTファイルを閉じる
    root_file.Close()

    print(f"Nuclear charts for Setting ID {setting_id} have been saved to {root_file_path}")

