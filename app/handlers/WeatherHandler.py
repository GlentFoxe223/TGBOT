import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

weather_API = os.getenv('weather_API')

class WeatherHandler:
    @staticmethod
    def weather(city, message):
        res=requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_API}&units=metric')
        if  res.status_code == 200:
            data = json.loads(res.text)
            temp=round(data['main']['temp'])  
            feels_temp=round(data['main']['feels_like'])
            wind_speed = data['wind']['speed']
            image = 'summer.png' if temp >= 10 else 'clowd.png'
            file = open('./static/images'+image, 'rb')
            return f'Погода:\nТемпература = {temp} градусов цельсия, ощущается как {feels_temp} градусов;\nСкорость ветра = {wind_speed} м/с'
        else:
            return 'Не удалось получить погоду'