import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from datetime import datetime
import pandas as pd


class SocialBladeTikTokScraper:
    def __init__(self):
        self.driver = None
        self.wait = None

    def parse_count(self,date: str) -> int:
        date_str = date.upper().strip()
        if date_str.endswith("K"):
            return int(float(date_str[:-1]) * 1_000)
        elif date_str.endswith("M"):
            return int(float(date_str[:-1]) * 1_000_000)
        else:
            return int(float(date_str))  # 小数だった場合にも対応
    
    def _setup_driver(self):
        """Chrome ドライバーを設定"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # ヘッドレスモード（ブラウザを開かない）
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")  # ヘッドレスモード用
        chrome_options.add_argument("--window-size=1920,1080")  # ヘッドレスモード用の画面サイズ
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # webdriver-manager を使用して自動的に適切な ChromeDriver をダウンロード・設定
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # ユーザーエージェントを設定
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def _close_driver(self):
        """ドライバーを閉じる"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
    
    async def get_user_data(self, username:str,tag:str):
        try:
            # ドライバーを設定
            self._setup_driver()
            
            # URLを構築してアクセス
            url = f"https://socialblade.com/tiktok/user/{username}"
            self.driver.get(url)
            
            # ページが完全に読み込まれるまで待機
            await asyncio.sleep(5)

            # データ抽出
            data = {}

            # ユーザー名の取得
            try:
                username_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3 span.truncate")))
                data["タグ"] = tag
                data["表示名"] = username_element.text
            except:
                try:
                    username_element = self.driver.find_element(By.XPATH, "//h3//span[contains(@class, 'truncate')]")
                    data["表示名"] = username_element.text
                except:
                    data["表示名"] = "※※※※※"

            # ユーザーIDの取得
            try:
                user_id_element = self.driver.find_element(By.CSS_SELECTOR, "h3 span.text-sm")
                data["ユーザーID"] = user_id_element.text.lstrip("@")
            except:
                try:
                    user_id_element = self.driver.find_element(By.XPATH, "//h3//span[contains(@class, 'text-sm')]")
                    data["ユーザーID"] = user_id_element.text.lstrip("@")
                except:
                    data["ユーザーID"] = "※※※※※"

            # デスクトップ版の統計情報を取得
            try:
                # フォロワー数（デスクトップ版）
                followers_desktop = self.driver.find_element(By.XPATH, "//p[text()='followers']/following-sibling::p[contains(@class, 'font-extralight')]")
                data["フォロワー"] =self.parse_count(followers_desktop.text) 
                
                # フォロー数（デスクトップ版）
                following_desktop = self.driver.find_element(By.XPATH, "//p[text()='following']/following-sibling::p[contains(@class, 'font-extralight')]")
                data["フォロー中"] = self.parse_count(following_desktop.text)
                
                # 動画数（デスクトップ版）
                videos_desktop = self.driver.find_element(By.XPATH, "//p[text()='videos']/following-sibling::p[contains(@class, 'font-extralight')]")
                data["動画数"] = self.parse_count(videos_desktop.text)

                # いいね数（デスクトップ版）
                likes_desktop = self.driver.find_element(By.XPATH, "//p[text()='likes']/following-sibling::p[contains(@class, 'font-extralight')]")
                data["総いいね数"] = self.parse_count(likes_desktop.text)
            except:
                return None

            # アカウント作成日の取得
            try:
                # デスクトップ版
                created_on_desktop = self.driver.find_element(By.XPATH, "//p[text()='Created On']/following-sibling::p[contains(@class, 'font-extralight')]")
                data["アカウント作成日"] = datetime.strptime(created_on_desktop.text, "%B %d, %Y").strftime("%Y/%m/%d")
            except:
                return None
            return data

        except Exception as e:
            print(f"エラーあああ: {e}")
            return None
        
        finally:
            self._close_driver()


# 使用例
async def main():
    scraper = SocialBladeTikTokScraper()
    
    # ユーザーデータを取得
    data = await scraper.get_user_data("dm_niki")
    
    # JSONとして表示
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # このファイルを直接実行した場合のテスト
    asyncio.run(main())