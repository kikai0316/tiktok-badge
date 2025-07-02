import requests
import os
from dotenv import load_dotenv

class Line:

    def send_line_message(self,message: str):
        load_dotenv()
        user_id=os.getenv('LINE_USER_ID')
        token=os.getenv('LINE_TOKEN')
    
        url = "https://api.line.me/v2/bot/message/push"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "to": user_id,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  
        except Exception as e:
            return
    
    def send_line_message_contact(self,is_group:bool,message: str):
        load_dotenv()
        user_id=os.getenv('LINE_USER_ID')
        group_id=os.getenv('LINE_GROUP_ID')
        token=os.getenv('LINE_TOKEN_CONTACT')
        to_id = group_id if is_group else user_id
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "to":  to_id,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  
        except Exception as e:
            return

# def main():
#     """使用例"""
#     Line().send_line_message_contact(True,"このグループへの接続が完了しました。次回の集計は、日本時間の12時20分ごろを予定しています。")
# if __name__ == "__main__":
#     main()