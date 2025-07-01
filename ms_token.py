import requests
import time
from google_sheet import GoogleSheet


class MSToken:
    def __init__(self):
        self.manager = GoogleSheet()

    def validate(self, ms_token: str) -> bool:
        """ms_tokenの有効性を検証"""
        if not ms_token or len(ms_token) < 50:
            return False

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.tiktok.com/'
        }

        try:
            response = requests.get(
                "https://www.tiktok.com/api/recommend/user_list/",
                params={'msToken': ms_token, 'count': 1},
                headers=headers,
                timeout=10
            )
            return response.status_code == 200 and 'status_code' in response.text
        except Exception as e:
            print(f"❌ バリデーションエラー: {e}")
            return False

    def fetch_from_selenium(self) -> str:
        """Seleniumでms_tokenを取得"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.tiktok.com")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        try:
            for cookie in driver.get_cookies():
                if cookie['name'] == 'msToken':
                    return cookie['value']
            raise Exception("msTokenが見つかりません")
        finally:
            driver.quit()



# # 使用例
# if __name__ == "__main__":
#     refresher = MSToken()
#     try:
#         token = refresher.ensure_valid_token()
#         print(f"✅ 有効なms_token: {token[:20]}...")
#     except Exception as e:
#         print(f"❌ エラー: {e}")
