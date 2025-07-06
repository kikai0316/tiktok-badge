from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, List, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import json

from line import Line


class Utils:
    def generate_daily_logs_id(self,base: str) -> list[str]:
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        one_month_ago = today - relativedelta(months=1)
        if today.day == 1:
            one_month_ago = today - relativedelta(months=1)
            one_month_ago = one_month_ago.replace(day=1) + relativedelta(months=1) - timedelta(days=1)

        # 日付をフォーマット
        def fmt(dt: datetime) -> str:
            return dt.strftime("%Y%m%d")

        return [
            f"{base}@{fmt(today)}",
            f"{base}@{fmt(yesterday)}",
            f"{base}@{fmt(one_month_ago)}",
        ]
    
    def enrich_log_data(self,              
        getdata: Dict[str, Any],
        yesterday_log: Optional[Dict[str, Any]],
        one_month_ago_log: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        try:
            enriched = getdata.copy()
            # 日付変換
            today = datetime.strptime(getdata["取得日時"], "%Y/%m/%d")
            created = datetime.strptime(getdata["アカウント作成日"], "%Y/%m/%d")

            # 動画 / 月（K列）
            month_diff = (today.year - created.year) * 12 + (today.month - created.month)
            enriched["動画 / 月"] = round(getdata["動画数"] / month_diff, 2) if month_diff > 0 else 0

            # いいね / 動画（L列）
            enriched["いいね / 動画"] = round(getdata["総いいね数"] / getdata["動画数"], 2) if getdata["動画数"] > 0 else 0

            # フォロワー前日比（M列）
            enriched["フォロワー前日比"] = (
                getdata["フォロワー"] - yesterday_log["フォロワー"]
                if yesterday_log else 0
            )

            # 動画数前日比（N列）
            enriched["動画数前日比"] = (
                getdata["動画数"] - yesterday_log["動画数"]
                if yesterday_log else 0
            )

            # 総いいね数前日比（O列）
            enriched["総いいね数前日比"] = (
                getdata["総いいね数"] - yesterday_log["総いいね数"]
                if yesterday_log else 0
            )

            # 動画/月前日比（P列）
            enriched["動画/月前日比"] = (
                enriched["動画 / 月"] - yesterday_log.get("動画 / 月", 0)
                if yesterday_log else 0
            )

            # いいね/動画前日比（Q列）
            enriched["いいね/動画前日比"] = (
                enriched["いいね / 動画"] - yesterday_log.get("いいね / 動画", 0)
                if yesterday_log else 0
            )

            # フォロワー前月比（R列）
            enriched["フォロワー前月比"] = (
                getdata["フォロワー"] - one_month_ago_log["フォロワー"]
                if one_month_ago_log else 0
            )

            # 動画 / 月 前月比（S列）
            enriched["動画 / 月 前月比"] = (
                enriched["動画 / 月"] - one_month_ago_log.get("動画 / 月", 0)
                if one_month_ago_log else 0
            )

            # いいね / 動画 前月比（T列）
            enriched["いいね / 動画 前月比"] = (
                enriched["いいね / 動画"] - one_month_ago_log.get("いいね / 動画", 0)
                if one_month_ago_log else 0
            )

            # 成長トレンドスコア（U列）
            def safe_ratio(n, d, w):
                try:
                    return (n / max(d, 0.1)) * w
                except ZeroDivisionError:
                    return 0

            score = (
                safe_ratio(enriched["フォロワー前日比"], getdata["フォロワー"], 50) +
                safe_ratio(enriched["動画数前日比"], getdata["動画数"], 10) +
                safe_ratio(enriched["総いいね数前日比"], getdata["総いいね数"], 15) +
                safe_ratio(enriched["動画/月前日比"], enriched["動画 / 月"], 5) +
                safe_ratio(enriched["いいね/動画前日比"], enriched["いいね / 動画"], 25)
            )

            enriched["成長トレンドスコア"] = round(min(10, max(-10, score)), 1)

            return enriched
        except Exception as e:
             lineManager = Line()
             lineManager.send_line_message(f"エラaaー：{str(e)}") 
    
    def get_top_trend_by_tag(self, documents_dict: dict) -> dict:        
        tag_groups = defaultdict(list)
        all_users = [] 
        for doc_id, user_data in documents_dict.items():
            tag = user_data.get("タグ", "").strip()
            if not tag:
                tag = "未分類"
            user_data_with_id = user_data.copy()
            user_data_with_id["document_id"] = doc_id
            user_data_with_id["original_tag"] = tag  

            base_tag = tag.split("@")[0].strip() if "@" in tag else tag
            tag_groups[base_tag].append(user_data_with_id)
            
            tag_groups[tag].append(user_data_with_id)
            
            all_users.append(user_data_with_id)
        
        result = {}
        
        # 各タググループのランキング
        for tag, users in tag_groups.items():
            sorted_users = sorted(
                users, 
                key=lambda x: x.get("成長トレンドスコア", 0), 
                reverse=True
            )
            result[tag] = sorted_users
        
        # 総合ランキング
        all_sorted = sorted(
            all_users,
            key=lambda x: x.get("成長トレンドスコア", 0),
            reverse=True
        )
        result["総合"] = all_sorted
        
        return result
    
    def to_top5_message(self, tag:str,ranking: List[dict]) -> str:
        emojis = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
        message=f"{tag}のスコアランキング\n"
        for i, (user_id,user_name, score, follower_diff, like_diff) in enumerate(ranking[:5]):
            if i!=0:
                message +="\n◇◇◇◇◇◇◇◇◇◇◇◇◇"
            message +=f"\n{emojis[i]}{user_id}\n🏷️{user_name}\n🔥{score} 👥{follower_diff:+} ❤️{like_diff:+}"
        return message
    
