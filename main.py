from ast import List, Str, Tuple
import asyncio
from google_sheet import GoogleSheet
from line import Line
from tiktok_original import SocialBladeTikTokScraper
import random
from datetime import datetime




def error_write(googleManager: GoogleSheet,userId:str,errorMesse:str,result:str) -> str:
        data={'取得日時': '', '取得結果': '❌', 'タグ': '', '表示名': '', 'ユーザーID': "", 'フォロワー': 0, 'フォロー中': 0, '動画数': 0, '総いいね数': 0, 'アカウント作成日': ''}
        data["取得日時"] = datetime.now().strftime("%Y/%m/%d").strip()
        data["取得結果"]=errorMesse
        data["ユーザーID"]=userId
        message= googleManager.write_user_data(data)
        if(message=="success"):
            return result
        else:
            print(message)
            return f"{result}＆WRITE_ERR"

def filter_user_ids_by_tag(
    all_users: List[Tuple[str, str]],
    tag: str
) -> List[str]:
    if "@" in tag:
        # 完全一致：例 → "自社@だいすけ"
        return [user_id for user_id, user_tag in all_users if user_tag == tag]
    else:
        # 部分一致（プレフィックスが一致）：例 → "自社" ⇒ "自社", "自社@だいすけ", ...
        return [user_id for user_id, user_tag in all_users if user_tag.startswith(tag)]

def aggregate_Message(googleManager: GoogleSheet,lineManager: Line,users: List[Tuple]) -> str:
        emojis = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
        aggregateTags=googleManager.get_aggregate_tags()
        for tags in aggregateTags:
            ranking=googleManager.get_today_user_metrics(filter_user_ids_by_tag(users,tags))
            ranking.sort(key=lambda x: x[1], reverse=True)
            message="f{tags}のスコアランキング\n\n"
            for i, (user_id, score, follower_diff, like_diff) in enumerate(ranking[:5]):
                message +=f"\n{emojis[i]} \n🔥{score} 👥{follower_diff:+} ❤️{like_diff:+}"
            lineManager.send_line_message_contact(message)
        return ""



async def main():
    lineManager=Line()
    googleManager=GoogleSheet()
    try:
        result_list=[]
        users=googleManager.get_all_users()
        if users:
            lineManager.send_line_message("⏱️ 本日のTikTokデータの定期取得の処理を開始いたしました")
            userIds = [user_id for user_id, _ in users]
            for userId in userIds:
                # wait_time = random.randint(1, 54)
                # await asyncio.sleep(wait_time)
                try:
                    socialBlade= SocialBladeTikTokScraper()
                    data = await socialBlade.get_user_data(userId)
                    if data:
                        message= googleManager.write_user_data(data)
                        if(message=="success"):
                            result_list.append("SUCCESS")
                        else:
                            result_list.append("WRITE_ERR")
                    else:
                        result= error_write(googleManager,userId,"❌｜取得失敗","DATA_ERR_FETCH")
                        result_list.append(result)

                except Exception as e:
                    result=error_write(googleManager,userId,f"❌｜実行中のエラー{e}","PROCESS_ERR")
                    result_list.append(result)
            
            resultMessage="✅ 本日のTikTokデータの定期取得の処理が終了しました\n"

            if all(result == "SUCCESS" for result in result_list):
                resultMessage += f"取得結果：{len(result_list)}/{len(users)}件の成功\nお疲れ様でした🎉🎉🎉"

            else:
                resultMessage += f"取得結果：{result_list.count('SUCCESS')}/{len(users)}件の成功 \nエラーの内訳は以下の内容です"
                from collections import Counter
                counts = Counter(result_list)
                for status, count in counts.items():
                    resultMessage +=f"{status}: {count}件\n"
            
            lineManager.send_line_message(resultMessage)
            aggregate_Message(googleManager,lineManager,users)


        else:
            lineManager.send_line_message("⚠️ 本日のTikTokデータの定期処理は実行されませんでした。理由：ユーザーリストの取得に失敗しました。")
        
    except Exception as e:
        lineManager.send_line_message("❌ 定期取得の処理で何らかのエラーが発生しました\n\nエラー内容は以下になります。")
        lineManager.send_line_message(str(e))
       

        




if __name__ == "__main__":
    asyncio.run(main())

