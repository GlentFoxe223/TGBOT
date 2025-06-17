import os
from dotenv import load_dotenv
import telebot
from telebot import types
import html
import re

load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)
BOT_TOKEN = os.getenv("BOT_API1")

if not BOT_TOKEN:
    raise RuntimeError("Одна из переменных BOT_API не задана в .env")

bot = telebot.TeleBot(BOT_TOKEN)

from db.DBsearcher import DBsearcher
from handlers.WeatherHandler import WeatherHandler
from handlers.NewsHandler import NewsHandler
from handlers.IIHandler import IIHandler

class BotCore:
    def __init__(self):
        self.db = DBsearcher('fullbotdata.db')

        self.main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [
            types.KeyboardButton('Погода'),
            types.KeyboardButton('Конвертация валют'),
            types.KeyboardButton('Новости'),
            types.KeyboardButton('ИИ помощник'),
        ]
        self.main_kb.add(*buttons)

        self.remove_kb = types.ReplyKeyboardRemove()
        self.user_pages = {}

        self.register_handlers()

        self.answer = IIHandler()

    def register_handlers(self):
        @bot.message_handler(commands=['start'])
        def cmd_start(message):
            user_id = message.from_user.id
            username = message.from_user.username
            self.db.add_user(user_id, username)
            bot.send_message(
                message.chat.id,
                "Привет! Выберите действие:",
                reply_markup=self.main_kb
            )

        @bot.message_handler(func=lambda m: m.text == 'Погода')
        def cmd_weather(message):
            msg = bot.send_message(
                message.chat.id,
                "Введите город:",
                reply_markup=self.remove_kb
            )
            bot.register_next_step_handler(msg, self.process_weather)

        @bot.message_handler(func=lambda m: m.text == 'Конвертация валют')
        def cmd_currency(message):
            bot.send_message(
                message.chat.id,
                "Конвертация валют в разработке…",
                reply_markup=self.main_kb
            )

        @bot.message_handler(func=lambda m: m.text == 'Новости')
        def cmd_news(message):
            user_id = message.from_user.id
            parser = NewsHandler()
            news = parser.get_news()
            if not news:
                bot.send_message(message.chat.id, "Не удалось получить новости.")
                return
            self.user_pages[user_id] = {
                'news': news,
                'page': 0
            }
            self.send_news_page(message.chat.id, user_id)

        @bot.message_handler(func=lambda m: m.text in ['Далее', 'Назад'])
        def news_navigation(message):
            user_id = message.from_user.id
            if user_id not in self.user_pages:
                bot.send_message(message.chat.id, "Сначала выберите раздел", reply_markup=self.main_kb)
                return
            if message.text == 'Далее':
                total_news = len(self.user_pages[user_id]['news'])
                current_page = self.user_pages[user_id]['page']
                if current_page < total_news - 1:
                    self.user_pages[user_id]['page'] += 1
                self.send_news_page(message.chat.id, user_id)
            elif message.text == 'Назад':
                self.user_pages.pop(user_id, None)
                bot.send_message(
                    message.chat.id,
                    "Возвращаемся в главное меню:",
                    reply_markup=self.main_kb
                )

        @bot.message_handler(func=lambda m: m.text == 'ИИ помощник')
        def cmd_ii(message):
            II_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons_for_II=[
            types.KeyboardButton('Назад'),
            # types.KeyboardButton('Очистить историю')
            ]
            II_kb.add(*buttons_for_II)
            bot.send_message(message.chat.id, 'Начните диалог с ИИ(обработка занимает время, поэтому после каждого запроса немного подождите)', reply_markup=II_kb)
            bot.register_next_step_handler(message, self.process_II)

        @bot.message_handler(func=lambda m: m.text == 'Назад')
        def cmd_back(message):
            bot.send_message(
                message.chat.id,
                "Возвращаемся в главное меню:",
                reply_markup=self.main_kb
            )

        @bot.callback_query_handler(func=lambda call: True)
        def handle_article_callback(call):
            news_url = call.data
            bot.answer_callback_query(call.id, "Открываю статью...")
            self.send_full_page(call.message.chat.id, news_url)

    def process_weather(self, message):
        city = message.text.strip()
        weather_text = WeatherHandler.get_weather(city)
        image = WeatherHandler.get_image(city)
        with open('./app/static/images/' + image, 'rb') as file:
            bot.send_photo(message.chat.id, file)
        bot.send_message(
            message.chat.id,
            weather_text,
            reply_markup=self.main_kb
        )

    def send_news_page(self, chat_id, user_id):
        page_data = self.user_pages[user_id]
        news = page_data['news']
        page = page_data['page']
        start = page * 10
        end = start + 10
        news_page = news[start:end]
        if not news_page:
            bot.send_message(chat_id, "Новостей больше нет.", reply_markup=self.main_kb)
            self.user_pages.pop(user_id, None)
            return
        total_news = len(news)
        for idx, item in enumerate(news_page, start=start + 1):
            text = f"{idx}. {item['title']}"
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Читать статью", callback_data=item['link'])
            markup.add(button)
            bot.send_message(chat_id, text, reply_markup=markup)
        if end >= total_news:
            bot.send_message(chat_id, "Новостей на сегодня больше нет.", reply_markup=self.main_kb)
            self.user_pages.pop(user_id, None)
        else:
            news_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            news_kb.add(types.KeyboardButton('Далее'), types.KeyboardButton('Назад'))
            bot.send_message(chat_id, "Хотите ещё новостей?", reply_markup=news_kb)

    def send_full_page(self, chat_id, news_url):
        parser = NewsHandler()
        article_paragraphs = parser.get_deep_news(news_url)
        article_text = "\n\n".join(article_paragraphs)
        cleaned_article_text = self.clean_words(article_text)
        article_text = html.unescape(cleaned_article_text)
        if len(article_text) > 4096:
            article_text = article_text[:4093] + "..."
        bot.send_message(
            chat_id,
            article_text,
            reply_markup=self.main_kb,
            parse_mode='HTML'
        )

    def clean_words(self, page):
        bad_url1 = os.getenv('bad_url1')
        bad_url2 = os.getenv('bad_url2')
        bad_url3 = os.getenv('bad_url3')
        bad_word1 = os.getenv('bad_word1')
        bad_word2 = os.getenv('bad_word2')
        bad_word3 = os.getenv('bad_word3')
        bad_word4 = os.getenv('bad_word4')
        bad_words = [bad_url1,bad_url2,bad_url3,bad_word1,bad_word2,bad_word3,bad_word4]
        pattern = r'\b(?:' + '|'.join(map(re.escape, bad_words)) + r')\b'
        clean_text = re.sub(r'https?://\S+|[@#]\w+|' + pattern, '', page)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text    
    
    def process_II(self, message):
        if message.text=='Назад':
            bot.send_message(
                message.chat.id,
                "Возвращаемся в главное меню:",
                reply_markup=self.main_kb
            )
        # elif message.text == 'Очистить историю':
        #     bot.send_message(
        #         message.chat.id,
        #         "Очищаем историю...",
        #     )
        #     self.answer.delete_history()
        #     bot.send_message(message.chat.id, 'Начните новую беседу с ИИ')
        #     bot.register_next_step_handler(message, self.process_II)
        else:
            if isinstance(message.text, str):
                response = self.answer.answerII(message.text)
                bot.send_message(message.chat.id, response)
                bot.register_next_step_handler(message, self.process_II)
            else:
                bot.send_message(message.chat.id, 'Введите текст')
                bot.register_next_step_handler(message, self.process_II)

if __name__ == '__main__':
    bot_core = BotCore()
    bot.infinity_polling()