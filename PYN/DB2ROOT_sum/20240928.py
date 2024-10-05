import sqlite3
import ROOT
from ROOT import TCanvas, TLatex, TH2F, TFile, TLegend, TBox
import os

ROOT.gROOT.SetBatch(True)

def fetch_isotope_data_and_symbols(db_path, setting_ids):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT 
        I.setting_id, 
        I.Z, 
        I.N, 
        I.isotope_name, 
        I.Yield, 
        I.percent1,
        S.Symbol 
    FROM 
        Isotopes I 
    JOIN 
        Settings S 
    ON 
        I.setting_id = S.id
    WHERE
        I.setting_id IN ({})
    """.format(','.join('?' for _ in setting_ids))

    cursor.execute(query, setting_ids)

    isotopes_by_setting_id = {}
    for row in cursor.fetchall():
        (setting_id, Z, N, isotope_name, yield_value, percent1, symbol) = row
        
        if setting_id not in isotopes_by_setting_id:
            isotopes_by_setting_id[setting_id] = {'isotopes': [], 'symbol': symbol}
        isotopes_by_setting_id[setting_id]['isotopes'].append(
            (Z, N, isotope_name, yield_value, percent1)
        )

    conn.close()
    return isotopes_by_setting_id

def create_nuclear_chart(isotopes_by_setting_id, output_path):
    Nmin, Nmax = 40, 84
    Zmin, Zmax = 35, 56

    c1 = ROOT.TCanvas("cNuclearChart", "Nuclear Chart (Multiple Settings)", 1200, 800)
    c1.SetLogz(1)
    c1.SetRightMargin(0.15)

    h2 = ROOT.TH2F("h2_NuclearChart", "Nuclear Chart (Multiple Settings);Neutron Number (N);Proton Number (Z)", 
                   Nmax-Nmin+1, Nmin-0.5, Nmax+0.5, Zmax-Zmin+1, Zmin-0.5, Zmax+0.5)

    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kMagenta, ROOT.kCyan, ROOT.kOrange, ROOT.kViolet, ROOT.kTeal]

    legend = ROOT.TLegend(0.85, 0.1, 0.95, 0.9)
    legend.SetHeader("Settings")

    text_objects = []
    boxes = []
    for i, (setting_id, data) in enumerate(isotopes_by_setting_id.items()):
        color = colors[i % len(colors)]
        isotopes = data['isotopes']
        symbol = data['symbol']

        box = ROOT.TBox(0, 0, 1, 1)
        box.SetFillColor(color)
        box.SetLineColor(color)
        legend.AddEntry(box, f"{symbol} (ID: {setting_id})", "f")
        boxes.append(box)  # Keep a reference to the box

        yield_sum = 0

        for isotope in isotopes:
            Z, N, isotope_name, yield_value, percent1 = isotope
            yield_sum += yield_value

        for isotope in isotopes:
            Z, N, isotope_name, yield_value, percent1 = isotope
            if yield_sum > 10000:
                yield_normal_factor = 10000 / yield_sum
            else:
                yield_normal_factor = 1

            yield_value *= yield_normal_factor
            
            if Nmin <= N <= Nmax and Zmin <= Z <= Zmax:
                bin_content = h2.GetBinContent(N-Nmin+1, Z-Zmin+1)
                h2.SetBinContent(N-Nmin+1, Z-Zmin+1, bin_content + 1)

                #latex = ROOT.TLatex(N, Z + 0.3, isotope_name)
                latex = ROOT.TLatex(N, Z + 0.3, f"#splitline{{{isotope_name}}}{{{yield_value:.0f}}}")
                latex.SetTextSize(0.025)
                #latex.SetTextColor(ROOT.kBlack)
                latex.SetTextColor(color)
                latex.SetTextAlign(22)
                text_objects.append(latex)

                #yield_text = ROOT.TLatex(N, Z - 0.2, f"{setting_id:.0f}")
                yield_text = ROOT.TLatex(N, Z - 0.2, f"{yield_value:.0f}")
                yield_text.SetTextSize(0.025)
                yield_text.SetTextColor(ROOT.kBlack)
                #yield_text.SetTextColor(color)
                yield_text.SetTextAlign(22)
                text_objects.append(yield_text)

    h2.Draw("COLZ")
    for text in text_objects:
        text.Draw()
    c1.SetGrid(1, 1)
    legend.Draw()
    c1.RedrawAxis()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    c1.Update()
    c1.SaveAs(output_path)
    print(f"Nuclear chart has been saved to {output_path}")

    # Clean up
    c1.Close()
    ROOT.gDirectory.Delete("h2_NuclearChart")
    for obj in text_objects + boxes:
        ROOT.gDirectory.Delete(obj.GetName())
    ROOT.gDirectory.Delete(legend.GetName())

if __name__ == "__main__":
    db_path = "./settings.db"
    setting_ids = [2, 11, 12, 13, 14]  # 指定された setting_id
    isotopes_by_setting_id = fetch_isotope_data_and_symbols(db_path, setting_ids)
    
    # 最初の setting_id とそのシンボルを取得
    first_setting_id = next(iter(isotopes_by_setting_id))
    first_symbol = isotopes_by_setting_id[first_setting_id]['symbol']
    
    # 出力パスを生成
    output_dir = f"./ROOT/BigRIPS_NoXX_136Xe_9999"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"9999.root")
    
    create_nuclear_chart(isotopes_by_setting_id, output_path)
