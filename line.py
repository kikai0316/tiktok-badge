from typing import Optional
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
    
    def send_line_message_contact(message: str,send_id: Optional[str] = None):
        load_dotenv()
        token=os.getenv('LINE_TOKEN_CONTACT')
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "to": send_id or os.getenv('LINE_USER_ID'),
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