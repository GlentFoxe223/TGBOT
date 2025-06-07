import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os
from dotenv import load_dotenv

load_dotenv()

proxy_address = os.getenv('proxy_address')
proxy_username = os.getenv('proxy_username')
proxy_password = os.getenv('proxy_password')
base_url = os.getenv('base_url')
proxies = {
    "http": f"http://{proxy_username}:{proxy_password}@{proxy_address}",
    "https": f"http://{proxy_username}:{proxy_password}@{proxy_address}"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
urlsfast=[]

class News():
    def search(message):
        response = requests.get(base_url, headers=headers, proxies=proxies, timeout=30, verify=False)  # Отключаем проверку SSL
        if response.status_code == 200:
            # Используем BeautifulSoup для парсинга HTML
            soup = BeautifulSoup(response, 'html.parser')
            # Находим блок с новостями
            news_div = soup.find('div', class_='news news_latest')  # Ищем конкретный класс новостей
            if news_div:
                ul_tag = news_div.find('ul')  # Ищем тег <ul> внутри найденного div
                if ul_tag:
                    news_data = []
                    # Ищем все <li> элементы с новостями
                    for li in ul_tag.find_all('li'):
                        link_tag = li.find('a', href=True)
                        if link_tag:
                            article_url = urljoin(base_url, link_tag['href'])  # Формируем абсолютный URL
                            urlsfast.append(article_url)
                            article_title = link_tag.get_text(strip=True)
                            news_data.append({'title': article_title, 'link': article_url})
                            return news_data
                else:
                    print("Не удалось найти тег <ul> с новостями.")
            else:
                print(message.chat.id,"Не удалось найти блок с новостями.")
            time.sleep(2)  # Задержка 2 секунды перед следующим запросом
        else:
            print(message.chat.id,"Не удалось получить страницу.")