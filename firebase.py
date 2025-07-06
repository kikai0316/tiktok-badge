from typing import Any, Dict, List, Optional, Tuple
import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime
import json
import asyncio
from tiktok_original import SocialBladeTikTokScraper
from utils import Utils
import json

class FirebaseTikTokManager:
    def __init__(self):
        self.db = None
        self.initialized = False

    def initialize(self):
        try:
            service_account_json_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
            service_account_info = json.loads(service_account_json_str)
            cred = credentials.Certificate(service_account_info)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'projectId': 'tiktok-data-887b0',
                    'storageBucket': 'tiktok-data-887b0.firebasestorage.app'
                })
            self.db = firestore.client()
            self.initialized = True
            return True
        except Exception as e:
            return False
    
    def get_all_users(self) -> List[Tuple[str, str]]:
        try:
            users_ref = self.db.collection('user')
            docs = users_ref.stream()

            user_list = []
            for doc in docs:
                user_id = doc.id
                data = doc.to_dict()
                tag = data.get("tag", "").strip() if data.get("tag") else ""
                user_list.append((user_id, tag))

            return user_list

        except Exception as e:
            return None
    
    def fetch_documents_by_ids(self, doc_ids: List[str]) -> Dict[str, Optional[dict]]:
        try:
            doc_refs = [self.db.collection("daily_logs").document(doc_id) for doc_id in doc_ids]
            docs = self.db.get_all(doc_refs)
            return {doc.id: doc.to_dict() if doc.exists else None for doc in docs}
        except Exception as e:
            return None
    
    def get_all_fetch_data(self) -> Dict[str, Dict[str, Any]]:
        try:
            fetch_ref = self.db.collection('send_account')
            docs = fetch_ref.stream()
            fetch_dict = {}
            for doc in docs:
                doc_data = doc.to_dict()
                fetch_dict[doc.id] = doc_data 
            return fetch_dict

        except Exception as _:
            return None
    
    def bulk_write(self, documents_dict: Dict[str, dict], collection_name: str = "daily_logs") -> bool:
        if not documents_dict:
            return True
        try:
            items = list(documents_dict.items())
            batch_size = 500  
            for i in range(0, len(items), batch_size):
                batch = self.db.batch()
                batch_items = items[i:i + batch_size]
                
                for doc_id, doc_data in batch_items:
                    doc_ref = self.db.collection(collection_name).document(doc_id)
                    batch.set(doc_ref, doc_data)
                
                batch.commit()
            return True
        except Exception as e:
            return False
    def update_user_tags(self, user_tag_map: dict[str, dict[str, str]]):
        if not self.initialized:
            raise RuntimeError("Firebase not initialized.")

        try:
            batch = self.db.batch()
            for user_id, data in user_tag_map.items():
                doc_ref = self.db.collection("users").document(user_id)
                batch.set(doc_ref, data, merge=True)  # merge=True で既存データを維持
            batch.commit()
            print("✅ 全ユーザーのタグを更新しました")
        except Exception as e:
            print(f"❌ Firestore 書き込みエラー: {e}")


# # 使用例
# async def main():
#     try:
#         fb = FirebaseTikTokManager()
#         ut= Utils()
#         if fb.initialize("serviceAccountKey.json"):
#             print("✅ 初期化成功")
#             scraper = SocialBladeTikTokScraper()
#             doc_ids=[]
#             users = fb.get_all_users()
#             for id, tag in users:
#                 ids=ut.generate_daily_logs_id(id)
#                 doc_ids.extend(ids)
#             documents=fb.fetch_documents_by_ids(doc_ids)
#             print(documents)

#             # data = await scraper.get_user_data("dm_niki")
#             # if data:

#             #     ids=ut.generate_daily_logs_id("dm_niki")
#             #     today_id= ids[0]
#             #     yesterday_log=fb.get_daily_log(ids[1]) 
#             #     one_month_ago_log=fb.get_daily_log(ids[2]) 
#             #     today_log=ut.enrich_log_data(data,yesterday_log,one_month_ago_log)
#             #     print(json.dumps(today_log, ensure_ascii=False, indent=2))
#             # else:
#             #     print("データ取得に失敗")
        
          
#             # today_log=ut.enrich_log_data(data,data_1,data_2)
#             # is_write= fb.write_daily_log("dm_niki@20250706", today_log)
#             # print(is_write)
#             # users = fb.get_all_users()
#             # for uid, tag in users:
#             #     print(f"User ID: {uid}, Tag: {tag}")
#         else:
#             print("❌ 初期化失敗")
       
        
#     except Exception as e:
#         print(f"❌ エラー: {e}")
#         print("serviceAccountKey.jsonファイルが正しく配置されているか確認してください。")

# if __name__ == "__main__":
#     # このファイルを直接実行した場合のテスト
#     asyncio.run(main())