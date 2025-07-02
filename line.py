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
        user_id="U7de59042ed6be5dc59133926d95d6aea"
        # os.getenv('LINE_USER_ID')
        group_id="C89ba7780d9e4720e9757d02fdb474fae"
        
        token="jbDcZ5OgkYaFXBr9qKY+WiGBA8uxIOd272tuDlRYXZVmmAC+oazWlSWpGpKR2HVLY31vX4U1RYT3+ziQ5mC5lBB/ygZRA6j+t4ICj8cRyrXLq/J9JqWkLT65Jh6SuXoapYEv/4120tgtHiMpUZCxQQdB04t89/1O/w1cDnyilFU="
        # os.getenv('LINE_TOKEN_CONTACT')
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