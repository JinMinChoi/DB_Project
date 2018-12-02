from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.parse
import datetime as dt
"""
needs.py는 키워드를 선택, url검색, 키워드 검색 시 날짜구분에 이용됨
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DBP.settings")
import django
django.setup()
from App.models import Data

class TwitterCrawling():
    keyword = ""

    def __init__(self):
        self.url1 = "https://twitter.com/search?f=tweets&vertical=default&q="
        #self.url2 = urllib.parse.quote_plus(", ".join(self.keyword))
        self.s_date = dt.date(year=2018, month=11, day=30)
        self.e_date = dt.date(year=2018, month=12, day=1)

    def InputKeyword(self, word):
        print("트위터에서 검색될 키워드 : ")
        self.keyword = word
        print("\"" + self.keyword + "\"")
        return self.connect_chrome()

    def connect_chrome(self):
        print("Connecting chrome to tweet !")
        self.url = str(self.url1 + self.keyword)

        # 드라이버 연결(Chrome)
        self.driver = webdriver.Chrome('C:/Users/User/Desktop/chromedriver.exe')
        # 암묵적으로 웹 자원 로드를 위해 2초까지 기다린다
        self.driver.implicitly_wait(2)

        # BeautifulSoup를 이용한 html 스크래핑
        self.driver.get(self.url + '%20since%3A' + str(self.s_date) + '%20until%3A' + str(self.e_date) + '&amp;amp;amp;amp;amp;amp;lang=ko')
        self.html = self.driver.page_source
        self.soup = BeautifulSoup(self.html, 'html.parser')

        return self.parse_twitter_text()

    def parse_twitter_text(self):
        print("Parsing tweet text !(max = 20)")
        # 내용 파싱(추출)
        lists = self.soup.find_all("p", {"class": "TweetTextSize"})
        data_title = {}

        # 보여짐
        for i in lists:
            data_title[i.text] = i.text
        self.driver.quit()
        return data_title
