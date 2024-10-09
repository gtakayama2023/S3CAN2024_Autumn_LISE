import os
import subprocess
import glob
import time

# 設定
SHARE_DIR = "./LPP/SHARE"
SH_SCRIPT = "./SH/lise2root.sh"

def main():
    # ディレクトリとスクリプトの存在チェック
    if not os.path.isdir(SHARE_DIR):
        print(f"エラー: {SHARE_DIR} ディレクトリが見つかりません")
        return

    if not os.path.isfile(SH_SCRIPT):
        print(f"エラー: {SH_SCRIPT} スクリプトが見つかりません")
        return

    # 01から14まで順番に処理
    for i in range(1, 15):
        num = f"{i:02d}"
        pattern = os.path.join(SHARE_DIR, f"BigRIPS_No{num}_136Xe_*.lpp")
        files = glob.glob(pattern)

        if not files:
            print(f"警告: No{num} に対応するファイルが見つかりません")
            continue

        file_path = files[0]  # パターンにマッチする最初のファイル
        print(f"処理中: {file_path}")

        try:
            # ファイルをコピー
            subprocess.run(['cp', file_path, './LPP/temp.lpp'], check=True)
            
            # スクリプトを実行
            print(f"実行中: {SH_SCRIPT}")
            subprocess.run([SH_SCRIPT], check=True)
            
            # 処理完了後の待機時間
            time.sleep(1)

        except subprocess.CalledProcessError as e:
            print(f"エラー: コマンド実行中にエラーが発生しました: {e}")
        except Exception as e:
            print(f"エラー: 予期せぬエラーが発生しました: {e}")

    # 後処理
    if os.path.exists('./LPP/temp.lpp'):
        try:
            os.remove('./LPP/temp.lpp')
            print("一時ファイル ./LPP/temp.lpp を削除しました")
        except Exception as e:
            print(f"警告: 一時ファイルの削除に失敗しました: {e}")

    print("すべての処理が完了しました")

if __name__ == "__main__":
    main()
