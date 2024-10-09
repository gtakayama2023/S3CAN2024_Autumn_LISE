import os
import shutil
import re

def is_valid_filename(filename):
    # ファイル名が数字のみで構成されているかチェック
    name_without_ext = os.path.splitext(filename)[0]
    return name_without_ext.isdigit()

def extract_info(filepath):
    try:
        # ファイルパスからBigRIPS番号と元素記号を抽出
        dir_name = os.path.dirname(filepath)
        parts = dir_name.split('_')
        if len(parts) < 4:  # BigRIPS_NoXX_136Xe_element の形式をチェック
            return None, None
        element = parts[-1]
        
        # ファイル名から数字を抽出
        filename = os.path.basename(filepath)
        if not is_valid_filename(filename):
            return None, None
        
        file_num = int(os.path.splitext(filename)[0])
        return file_num, element
    except (ValueError, IndexError):
        return None, None

def create_new_filename(file_num, element):
    return f"BigRIPS_No{file_num:02d}_136Xe_{element}.lpp"

def main():
    print("現在の作業ディレクトリ:", os.getcwd())
    
    if not os.path.exists('SHARE'):
        os.makedirs('SHARE')
        print("SHARE ディレクトリを作成しました")

    processed_files = 0
    skipped_files = 0

    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.lpp'):
                filepath = os.path.join(root, file)
                
                # SHARE ディレクトリ内のファイルはスキップ
                if 'SHARE' in filepath.split(os.path.sep):
                    continue
                
                file_num, element = extract_info(filepath)
                
                if file_num is None or element is None:
                    print(f"スキップ: {filepath} (不適切なファイル名またはディレクトリ構造)")
                    skipped_files += 1
                    continue
                
                new_filename = create_new_filename(file_num, element)
                new_filepath = os.path.join('SHARE', new_filename)
                
                try:
                    shutil.copy2(filepath, new_filepath)
                    print(f"コピー完了: {filepath} -> {new_filepath}")
                    processed_files += 1
                except Exception as e:
                    print(f"エラー: {filepath} のコピー中に問題が発生しました - {str(e)}")
                    skipped_files += 1

    print(f"\n処理完了:")
    print(f"成功: {processed_files} ファイル")
    print(f"スキップ: {skipped_files} ファイル")

if __name__ == "__main__":
    main()
