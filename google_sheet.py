import json
import os
import gspread
from google.oauth2.service_account import Credentials
from typing import Any, Dict, List, Optional
import time
from dotenv import load_dotenv

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
    

    def get_all_users(self) -> List[str]:
        """all_users シートの A列2行目以降からすべての ms_token を取得"""
        try:
            all_users_ws = self.spreadsheet.worksheet("@all_users")  # all_users シートを取得
            col_values = all_users_ws.col_values(1)  # A列

            all_users = [v.strip() for v in col_values[1:] if v.strip()]
            return all_users
    
        except Exception as e:
            print(e)
            return None

    
    def write_user_data(self, user_data: Dict[str, Any]) -> str:
        print("ser_dat")
        sheet_name = user_data.get("ユーザーID")
        if not sheet_name:
            return "表示名が指定されていません"

        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            try:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")
            except Exception as e:
                return f"シート作成に失敗しました: {e}"

        try:
            existing_headers = worksheet.row_values(1)
            if not existing_headers:
                headers = list(user_data.keys())
                worksheet.update("A1", [headers])
            else:
                headers = existing_headers
        except Exception as e:
            return f"ヘッダー確認失敗: {e}"

        # 値を headers に合わせて並べる（空欄補完含む）
        values = [user_data.get(h, "") for h in headers]

        try:
            next_row = len(worksheet.get_all_values()) + 1
            worksheet.update(f"A{next_row}", [values])
            return "success"
        except Exception as e:
            return f"データ書き込み失敗（シート: {sheet_name}）: {e}"


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