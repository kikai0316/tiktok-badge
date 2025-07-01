
import asyncio
from datetime import datetime
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from typing import Any, Dict, List, Tuple
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
    

    def get_all_users(self) -> List[Tuple[str, str]]:
        try:
            all_users_ws = self.spreadsheet.worksheet("@all_users")  # @all_users シートを取得
            user_ids = all_users_ws.col_values(1)  # A列: ユーザーID
            tags = all_users_ws.col_values(2)      # B列: タグなど（例: 自社, 競合 など）

            # 2行目以降を対象（1行目はヘッダー想定）
            all_users = [
                (user_id.strip(), tag.strip())
                for user_id, tag in zip(user_ids[2:], tags[2:])
                if user_id.strip()
            ]
            return all_users

        except:
            return None
    
    def get_aggregate_tags(self) -> List[str]:
        try:
            all_users_ws = self.spreadsheet.worksheet("@all_users")  # @all_users シートを取得
            d_column_values = all_users_ws.col_values(4)  # D列を取得

            # 2行目以降を対象（1行目はヘッダー想定）
            all_users = [
                value.strip()
                for value in d_column_values[1:]  # インデックス1から（2行目以降）
                if value.strip()  # 空でない値のみ
            ]
            return all_users

        except:
            return None
    
    def get_today_user_metrics(self, user_ids: List[str]) -> List[Tuple[str, float, float, float]]:
        today = datetime.today().strftime('%Y/%m/%d')
        results = []

        for user_id in user_ids:
            try:
                ws = self.spreadsheet.worksheet(user_id)
                all_dates = ws.col_values(1)  # A列: 取得日時
                all_status = ws.col_values(2)  # B列: 取得結果（✅ など）

                # 今日 & ✅ の行を探す（2行目以降）
                row_index = None
                for i, (date, status) in enumerate(zip(all_dates[1:], all_status[1:]), start=2):
                    if date.strip() == today and status.strip() == "✅":
                        row_index = i
                        break

                if row_index is None:
                    print(f"Skipped {user_id}: no valid row for {today}")
                    continue

                # 指定列のデータ取得
                score = ws.cell(row_index, 21).value  # U列
                follower_diff = ws.cell(row_index, 13).value  # M列
                like_diff = ws.cell(row_index, 15).value      # O列

                def to_float(value):
                    try:
                        return float(value)
                    except:
                        return None

                results.append((
                    user_id,
                    to_float(score),
                    to_float(follower_diff),
                    to_float(like_diff)
                ))

            except Exception as e:
                print(f"Error processing {user_id}: {e}")
                continue

        return results

    
    async def write_user_data(self, user_data: Dict[str, Any]) -> str:
        print("ser_dat")
        sheet_name = user_data.get("ユーザーID")
        if not sheet_name:
            return "表示名が指定されていません"

        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            try:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
                await asyncio.sleep(5)
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