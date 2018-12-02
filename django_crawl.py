import first_tweet_new
import second_DOTAX
import third_JB

import datetime as dt
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DBP.settings")
import django
django.setup()
from App.models import Data

class DB():
    tweet_content = ""
    dotax_content = ""
    jb_content = ""
    flag = 1

    Tweet = first_tweet_new.TwitterCrawling()
    Dotax = second_DOTAX.DotaxCrawling()
    Jb = third_JB.JBCrawling()

    text_all = ""
    text_community = ""
    text_time = ""

    keyword = ""
    outlier = 0

    def tw(self, text_tw):
        for text in text_tw.items():
            tweet_Data = Data(text=text, community="트위터", time=dt.datetime.today().strftime("%Y.%m.%d"))
            tweet_Data.save()

    def dt(self, text_dt):
        for text in text_dt:
            dotax_Data = Data(text=text, community="도탁스", time=dt.datetime.today().strftime("%Y.%m.%d"))
            dotax_Data.save()

    def jb(self, text_jb):
        for text in text_jb:
            jjook_Data = Data(text=text, community="쭉빵", time=dt.datetime.today().strftime("%Y.%m.%d"))
            jjook_Data.save()

    def Input_Keyword(self):
        print("검색할 키워드를 검색하시오 : ")
        self.keyword = input()
        return self.GetOutlier()

    def GetOutlier(self):
        print("=====커뮤니티 쭉빵 카페 진입=====")
        jb_outlier = self.Jb.GetOutlier(self.keyword)
        print("=====커뮤니티 도탁스 카페 진입=====")
        dt_outlier = self.Dotax.GetOutlier(self.keyword)
        self.outlier = 1 #dt_outlier if jb_outlier > dt_outlier else jb_outlier
        return self.CompareOLSC()

    def CompareOLSC(self):  # OL : Outlier, SC : Search_Cnt
        if self.outlier <= self.Dotax.GetSearchCount(self.keyword) or self.outlier <= self.Jb.GetSearchCount(self.keyword):
            self.DB_save()
        else:
            print("outlier({0})보다 적은 게시물이 등록되어 있습니다.".format(self.outlier))
            print("아웃라이어보다 작아서 종료")

    def DB_save(self):
        print("outlier({0})보다 많은 게시물이 등록되어 있습니다.".format(self.outlier))
        text_data_tweet = self.Tweet.InputKeyword(self.keyword)
        self.tw(text_data_tweet)

        self.Dotax.InputKeyword(self.keyword)
        self.dt(self.Dotax.text)

        self.Jb.InputKeyword(self.keyword)
        self.jb(self.Jb.text)

        cnt = 1
        for all_text in Data.objects.all():
            if all_text.community == "트위터" :
                self.tweet_content += str(cnt) + "\t" + all_text.text + "\t" + all_text.community + "\n"
                filename = str(all_text.community) + str(all_text.time)
                file1 = open(filename, 'w', encoding='utf-8')
                file1.write(self.tweet_content)

            if all_text.community == "도탁스":
                if self.flag == 1:
                    file1.close()
                    self.flag = 2
                self.dotax_content += str(cnt) + "\t" +  all_text.text + "\t" + all_text.community + "\n"
                filename = str(all_text.community) + str(all_text.time)
                file2 = open(filename, 'w', encoding='utf-8')
                file2.write(self.dotax_content)

            elif all_text.community == "쭉빵":
                if self.flag == 2:
                    file2.close()
                    self.flag = 3
                self.jb_content += str(cnt) + "\t" +  all_text.text + "\t" + all_text.community + "\n"
                filename = str(all_text.community) + str(all_text.time)
                file3 = open(filename, 'w', encoding='utf-8')
                file3.write(self.jb_content)
            cnt += 1
        file3.close()

if __name__ == '__main__':
    DB().Input_Keyword()
