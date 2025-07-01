import asyncio
import argparse
from TikTokApi import TikTokApi

from ms_token import MSToken



class TikTok:
    def __init__(self, ms_token: str):
        self.ms_token = ms_token
        self.api = None
    
    async def __aenter__(self):
        self.api = TikTokApi()
        await self.api.create_sessions(ms_tokens=[self.ms_token], num_sessions=1,  headless=False,  # ヘッドレスを無効にして検出を回避
                browser="webkit",
                sleep_after=5)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.api:
            await self.api.close_sessions()
    
    def _safe_int(self, value) -> int:
        try:
            return int(str(value).replace(',', '')) if value else 0
        except:
            return 0
    
    async def get_user_data(self, username: str, video_count: int = 50):
        try:
            user = self.api.user(username=username)
            info = await user.info()
            
            # データ抽出
            if "userInfo" in info:
                user_data = info["userInfo"]["user"]
                stats = info["userInfo"].get("statsV2") or info["userInfo"].get("stats", {})
            else:
                user_data = info.get("user", info)
                stats = {}
            
            # 基本情報
            result = {
                "ユーザー名": user_data.get('uniqueId', username),
                "表示名": user_data.get('nickname', 'N/A'),
                "フォロワー": self._safe_int(stats.get('followerCount')),
                "フォロー中": self._safe_int(stats.get('followingCount')),
                "動画数": self._safe_int(stats.get('videoCount')),
                "総いいね": self._safe_int(stats.get('heartCount')),
            }
            
            # 動画統計
            total_views = total_likes = total_shares = 0
            try:
                async for video in user.videos(count=video_count):
                    video_stats = getattr(video, 'stats', {})
                    total_views += self._safe_int(video_stats.get('playCount'))
                    total_likes += self._safe_int(video_stats.get('diggCount'))
                    total_shares += self._safe_int(video_stats.get('shareCount'))
            except:
                pass
            
            result.update({
                "総再生数": total_views,
                "動画いいね": total_likes,
                "総シェア": total_shares
            })
            
            return result
            
        except Exception as e:
            print(f"エラー: {e}")
            return None
    
    def print_result(self, data):
        if not data:
            return
        print("\n結果:")
        for key, value in data.items():
            print(f"{key}: {value:,}" if isinstance(value, int) else f"{key}: {value}")

# async def main():
#    VIDEO_COUNT = 50
#    USERNAME = "dshengtian6"
#    refresher = MSToken()
   
#    try:
#        token = refresher.ensure_valid_token()
#        print(f"✅ 有効なms_token: {token[:20]}...")
       
#        async with TikTokScraper(token) as scraper:
#            data = await scraper.get_user_data(USERNAME, VIDEO_COUNT)
#            scraper.print_result(data)
           
#    except Exception as e:
#        print(f"❌ エラー: {e}")

# if __name__ == "__main__":
#     asyncio.run(main())