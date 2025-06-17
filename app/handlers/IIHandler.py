from g4f.client import Client
from g4f import models
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)

class IIHandler:
    def __init__(self):
        self.client = Client()
        # self.history = {}
        # self.user=os.getenv('proxy_username')
        # self.password=os.getenv('proxy_password')
        # self.host=os.getenv('proxy_address')
        # self.proxy=f"http://{self.user}:{self.password}@{self.host}"

    def answerII(self, text):
        # if user_id not in self.history:
            # self.history[user_id] = []
        # self.history[user_id].append({"role": "user", "content": text})
        # self.trim_history(user_id)
        response = self.client.chat.completions.create(
            text,
            model=models.default,
            web_search=False
        )
        if response and len(response.choices) > 0:
            # self.history[user_id].append({"role": "assistant", "content": answer})
            return response.choices[0].message.content
        else:
            return 'ИИ не дал ответа'

    # def trim_history(self, user_id, max_length=4096):
    #     if user_id not in self.history:
    #         return
    #     current_length = sum(len(m["content"]) for m in self.history[user_id])
    #     while self.history[user_id] and current_length > max_length:
    #         removed = self.history[user_id].pop(0)
    #         current_length -= len(removed["content"])

    # def delete_history(self, user_id):
    #     self.history[user_id] = []

    def get_answer(self, user_id, text):
        return self.answerII(user_id, text)