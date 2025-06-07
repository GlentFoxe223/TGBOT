import telebot
from telebot import types
import os
from dotenv import load_dotenv
from db import DBsearcher as DB
from handlers import WeatherHandler as Weather
from handlers import NewsHandler as News
from handlers import IIHandler as II
from handlers import CurrencyHandler as Currency


load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT_API"))
a = types.ReplyKeyboardRemove()

class bot_heart:
    def __init__(self):
        self.db = DB('fullbotdata.db')

    def rm(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons=[
            types.KeyboardButton('Погода'),
            types.KeyboardButton('Конвертация валют'),
            types.KeyboardButton('Новости'),
            types.KeyboardButton('ИИ помощник')
        ]
        keyboard.add(*buttons)
        return keyboard
    
    def start(self, message):
        user_id = message.from_user.id
        username = message.from_user.username or None
        self.db.add_user(user_id, username)
        bot.send_message(message.chat.id, 'Привет, нажмите на кнопку', reply_markup=self.rm())

    def handle_weather(self, message):
        msg = bot.send_message(message.chat.id, 'Введите город', reply_markup=a)
        bot.register_next_step_handler(msg, self.process_weather)

    def process_weather(self, message):
        city = message.text.strip().lower()
        result = Weather.weather(city, message)
        bot.send_message(message.chat.id, result, reply_markup=self.mm())

    # def handle_news(self, message):
    #     bot.send_message(message.chat.id, 'Поиск новостей...',  reply_markup=newsnext)
    #     global newsdata
    #     global noofnews
    #     global fromnews
    #     global tonews
    #     newsdata = News.search(message)
    #     if newsdata:
    #         for news in newsdata[fromnews:tonews:]:
    #             bot.send_message(message.chat.id,f"{noofnews}.{news['title'][4::]}")
    #             noofnews += 1
    #         bot.register_next_step_handler(self.process_news)
    #     else:
    #         bot.send_message(message.chat.id, 'Ошибка')

my_bot=bot_heart()

@bot.message_handler(commands=['start'])
def true_start(message):
    my_bot.start(message)

@bot.message_handler(func=lambda message: message.text == 'Погода')
def true_weather_handler(message):
    my_bot.handle_weather(message)

@bot.message_handler(func=lambda message: message.text == 'Конвертация валют')
def true_currency_handler(message):
#     my_bot.handle_currency(message)
    bot.send_message(message.chat.id, 'In work')

@bot.message_handler(func=lambda message: message.text == 'Новости')
def true_news_handler(message):
    my_bot.handle_news(message)

@bot.message_handler(func=lambda message: message.text == 'ИИ помощник')
def true_II_handler(message):
#     my_bot.handle_II
    bot.send_message(message.chat.id, 'In work')

@bot.message_handler(func=lambda message: message.text == 'Назад')
def reset(message):
    my_bot.start(message)
    # bot.register_next_step_handler(message, true_start)
# @bot.message_handler(func=lambda message: message.text == 'Далее')
# def next(message):
#         global fromnews
#         global tonews
#         global noofnews
#         fromnews+=10
#         tonews+=10
#         for news in newsdata['title'][fromnews:tonews:]:
#             bot.send_message(message.chat.id,f"{noofnews}.{news['title'][4::]}")
#             noofnews += 1
#         if fromnews == 40:
#             fromnews = 0
#             tonews = 9
#             noofnews = 1
#             msg = bot.send_message(message.chat.id, 'Новостей больше нет')
#             bot.register_next_step_handler(msg, true_start)

# @bot.message_handler(func=lambda message: message.text == 'Назад')
# def reset(message):
#     bot.register_next_step_handler(message, true_start)

bot.infinity_polling()