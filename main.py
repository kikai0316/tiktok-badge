
import asyncio
import random
from typing import List, Tuple
from firebase import FirebaseTikTokManager
from google_sheet import GoogleSheet
from line import Line
from tiktok_original import SocialBladeTikTokScraper
from datetime import datetime

from utils import Utils
import time
from collections import Counter

async def main():
    lineManager = Line()
    fb = FirebaseTikTokManager()
    gs = GoogleSheet()
    scraper = SocialBladeTikTokScraper()
    ut = Utils()
    results = {}
    errors = {}
    doc_ids = []
    start_time = time.time()
    lineManager.send_line_message("⚠️ テスト開始")
    data=gs.get_all_users_tag_map()
    lineManager.send_line_message(f"取得数：{len(data.values())}")
    fb.initialize()
    fb.update_user_tags(data)
    lineManager.send_line_message("⚠️ 成功")
    # try:
    #     if not fb.initialize():
    #         lineManager.send_line_message("⚠️ 本日のTikTokデータの定期処理は実行されませんでした。\n\n理由：\nFireBase接続エラー")
    #         return
    #     users = fb.get_all_users() 
    #     if not users:
    #         lineManager.send_line_message("⚠️ 本日のTikTokデータの定期処理は実行されませんでした。\n\n理由：\nユーザーリストの取得に失敗しました。")
    #         return
        
    #     lineManager.send_line_message("⏱️ 本日のTikTokデータの定期取得の処理を開始いたしました")  # awaitを追加
        
    #     # まとめて昨日と１っヶ月前のデータを取得する
    #     for id, _ in users:
    #         ids = ut.generate_daily_logs_id(id) 
    #         ids = ids[1:]
    #         doc_ids.extend(ids)
    #     documents = fb.fetch_documents_by_ids(doc_ids) 
        
    #     # 今日のデータ、昨日、１っヶ月前のデータをもとに、今日の記録を作成する
    #     for id, tag in users:
    #         ids = ut.generate_daily_logs_id(id) 
    #         wait_time = random.randint(1, 29)
    #         await asyncio.sleep(wait_time)
    #         data = await scraper.get_user_data(id, tag)
    #         if not data:
    #             today = datetime.now().strftime("%Y%m%d")
    #             errors[f"{today}/{id}"] = {"code": "FETCH_ERROR", "message": "スクレイピングの取得の時にエラーが発生しました"}
    #             continue 
    #         today_id = ids[0]
    #         yesterday_log = documents.get(ids[1])  
    #         one_month_ago_log = documents.get(ids[2])  
    #         today_log = ut.enrich_log_data(data, yesterday_log, one_month_ago_log)
    #         results[today_id] = today_log
    #     # 取得成功と失敗時のログをfirebaseに保存する
    #     if results:
    #         if not fb.bulk_write(results): 
    #             lineManager.send_line_message("❌書き込みエラー\n成功したデータの書き込みに失敗しました")
        
    #     if errors:
    #         if not fb.bulk_write(errors, "error_logs"): 
    #             lineManager.send_line_message("❌書き込みエラー\nエラーログのデータの書き込みに失敗しました")

    #     top_trend = ut.get_top_trend_by_tag(results) 
    #     # スプレットシートに集計結果だけを記録する
    #     success = await gs.write_ranking_data(top_trend)
    #     if not success:
    #         lineManager.send_line_message("❌スプレットシート書き込みエラー\nスプレットシートの書き込みに失敗しました。")
    #     # 結果（白）のアカウントに集計の結果を送信する
        
    #     send_accounts = fb.get_all_fetch_data() 
    #     if send_accounts:
    #         for account_data in send_accounts.values():
    #             send_id = account_data.get("id")
    #             tags = account_data.get("tags") 
    #             lineManager.send_line_message_contact("✅昨日のTikTokインサイト自動解析システムによる集計が完了しました。",send_id)
    #             if tags:
    #                 # タグのListがあれば、そのタグだけを送信する
    #                 for tag in tags:
    #                     if tag not in top_trend:
    #                         continue
    #                     message = ut.to_top5_message(tag, top_trend[tag])
    #                     lineManager.send_line_message_contact(message, send_id) 
    #             else:
    #                 # タグのListがなければ、全てのタグを返す
    #                 for tag in top_trend.keys():
    #                     message = ut.to_top5_message(tag, top_trend[tag])
    #                     lineManager.send_line_message_contact(message, send_id) 
    #     else:
    #         lineManager.send_line_message_contact("❌送信先のアカウント取得に失敗しました") 
    #     # システム（黒）に処理の結果を送信する
    #     resultMessage = "✅ 本日のTikTokデータの定期取得の処理が終了しました\n"
    #     if len(results.keys()) == len(users):
    #         resultMessage += f"取得結果：{len(results.keys())}/{len(users)}件の成功\nお疲れ様でした🎉🎉🎉"
    #     else:
    #         resultMessage += f"取得結果：{len(results.keys())}/{len(users)}件の成功 \nエラーの件数：{len(errors.keys())}件"

    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     resultMessage += f"\n\n処理時間：{int(elapsed_time // 60)}分{int(elapsed_time % 60)}秒"

    #     lineManager.send_line_message(resultMessage)
    # except Exception as e:
    #     lineManager.send_line_message("❌ 定期取得の処理で何らかのエラーが発生しました\n\nエラー内容は以下になります。") 
    #     lineManager.send_line_message(str(e))
    
       

        




if __name__ == "__main__":
    asyncio.run(main())

