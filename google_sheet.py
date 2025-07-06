
from datetime import datetime
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv
import requests

# =============================================================================
# 設定
# =============================================================================

class GoogleSheet:
    def __init__(self):
        # 認証
        scope = ['https://spreadsheets.google.com/feeds', 
                'https://www.googleapis.com/auth/drive']
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        service_account_json_str = os.getenv("SERVICE_ACCOUNT_JSON")
        if not service_account_json_str:
            raise ValueError("環境変数 SERVICE_ACCOUNT_JSON が設定されていません")
        service_account_info = json.loads(service_account_json_str)
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
        gc = gspread.authorize(credentials)
        self.spreadsheet = gc.open_by_key(spreadsheet_id)
        

    async def write_ranking_data(self, ranking_data: Dict[str, List[Dict[str, Any]]]) -> bool:
        COLUMN_ORDER = [
            "取得日時",           # A
            "タグ",              # B  
            "表示名",            # C
            "ユーザーID",         # D
            "フォロワー",         # E
            "フォロー中",         # F
            "動画数",            # G
            "総いいね数",         # H
            "アカウント作成日",    # I
            "動画 / 月",         # J
            "いいね / 動画",      # K
            "フォロワー前日比",    # L
            "動画数前日比",       # M
            "総いいね数前日比",    # N
            "動画/月前日比",      # O
            "いいね/動画前日比",   # P
            "フォロワー前月比",    # Q
            "動画 / 月 前月比",   # R
            "いいね / 動画 前月比", # S
            "成長トレンドスコア"   # T
        ]
        
        for tag_name, user_list in ranking_data.items():
            try:
                # シート取得または作成
                sheet_name = tag_name
                try:
                    worksheet = self.spreadsheet.worksheet(sheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    try:
                        worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
                    except Exception:
                        return False
                
                # ヘッダー設定
                try:
                    existing_headers = worksheet.row_values(1)
                    if not existing_headers or existing_headers != COLUMN_ORDER:
                        worksheet.update("A1", [COLUMN_ORDER])
                except Exception:
                    return False
                
                # 既存データをクリア（ヘッダー以外）
                try:
                    existing_data = worksheet.get_all_values()
                    if len(existing_data) > 1:
                        clear_range = f"A2:T{len(existing_data)}"
                        worksheet.batch_clear([clear_range])
                except Exception:
                    return False
                
                # データ準備
                data_rows = []
                for user_data in user_list:
                    row_data = []
                    for column in COLUMN_ORDER:
                        value = user_data.get(column, "")
                        if isinstance(value, (int, float)):
                            row_data.append(str(value))
                        else:
                            row_data.append(str(value) if value is not None else "")
                    data_rows.append(row_data)
                
                # データ書き込み
                if data_rows:
                    try:
                        range_name = f"A2:T{len(data_rows) + 1}"
                        worksheet.update(range_name, data_rows)
                    except Exception:
                        return False
            
            except Exception:
                return False
        
        return True

def main():
    """使用例"""

    # test_user_data = {
    #     "ユーザーID": "test_121",
    #     "表示名": "DMニキ",
    #     "フォロワー": 0,
    #     "フォロー中": 0,
    #     "作成日": "N/A",
    #     "動画数": 0,
    #     "総再生数": 9183900,
    #     "総いいね数": 187891,
    #     "総シェア数": 1925
    # }

    # writer = GoogleSheet()
    # message= writer.write_user_data(test_user_data)
    # print(message)
    # manager = MSTokenManager()
    # users = manager.get_all_users()
    # print(f"取得した:${users}")

    # manager = MSTokenManager()
    # current_token = manager.get_ms_token()
    # print(f"現在のms_token: {current_token[:20] if current_token else 'なし'}...")
    
    # # 新しいms_tokenを設定（例）
    # new_token = "new_ms_token_example_12345"
    # success = manager.set_ms_token(new_token)
    # print(f"ms_token更新: {'成功' if success else '失敗'}")
    
    # # 確認
    # updated_token = manager.get_ms_token()
    # print(f"更新後のms_token: {updated_token[:20] if updated_token else 'なし'}...")

if __name__ == "__main__":
    main()