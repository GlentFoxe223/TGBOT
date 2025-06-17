import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString, Tag
from urllib.parse import urljoin
import os
from dotenv import load_dotenv
import re

class NewsHandler:
    def __init__(self):
        load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)

        self.base_url = os.getenv('base_url')
        proxy_address = os.getenv('proxy_address')
        proxy_username = os.getenv('proxy_username')
        proxy_password = os.getenv('proxy_password')

        self.proxies = {
            "http": f"http://{proxy_username}:{proxy_password}@{proxy_address}",
            "https": f"http://{proxy_username}:{proxy_password}@{proxy_address}"
        }

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_page(self):
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=30,
                verify=False
            )
            if response.status_code == 200:
                return response.text
            else:
                print(f"[Ошибка] Код ответа: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[Ошибка запроса] {e}")
        return None

    def parse_news(self, html):
        news_data = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            news_div = soup.find('div', class_='news news_latest')
            if news_div:
                ul_tag = news_div.find('ul')
                if ul_tag:
                    for li in ul_tag.find_all('li'):
                        link_tag = li.find('a', href=True)
                        if link_tag:
                            title = link_tag.get_text(strip=True)
                            url = urljoin(self.base_url, link_tag['href'])
                            if title and url:
                                news_data.append({'title': title, 'link': url})
        except Exception as e:
            print(f"[Ошибка парсинга новостей] {e}")
        return news_data
    
    def get_images(self, html):
        None

    def get_news(self):
        html = self.fetch_page()
        if html:
            return self.parse_news(html)
        return []

    def fetch_deep_page(self, url):
        try:
            response = requests.get(
                url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=30,
                verify=False
            )
            if response.status_code == 200:
                return response.text
            else:
                print(f"[Ошибка] Код ответа: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[Ошибка запроса] {e}")
        return None

    def parse_deep_news(self, html):
        deep_news = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            article_tag = soup.find('div', class_='l-main')
            if article_tag:
                content = article_tag.find('article', class_='article')
                if content:
                    for p in content.find_all('p'):
                        cleaned = self.clean_html_tags(p)
                        if cleaned:
                            
                            deep_news.append(cleaned)
        except Exception as e:
            print(f"[Ошибка парсинга статьи] {e}")
        return deep_news
    
    def get_deep_images(self):
        None

    def clean_html_tags(self, tag):
        allowed_tags = {'b', 'strong', 'i', 'em', 'u', 's', 'strike', 'del', 'code', 'pre'}
        allowed_attrs = {'href'}
        for t in tag.find_all(True):
            if t.name not in allowed_tags:
                t.unwrap()
            else:
                t.attrs = {k: v for k, v in t.attrs.items() if k in allowed_attrs}
                if t.name == 'a' and 'href' not in t.attrs:
                    t.unwrap()
        return tag.decode_contents(formatter="html")    

    def get_deep_news(self, url):
        html = self.fetch_deep_page(url)
        if html:
            return self.parse_deep_news(html)
        return []