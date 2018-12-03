import lxml.html
import requests
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import datetime
import numpy as np  # numpy : 아웃라이어 라이브러리

"""
참고 사이트 : https://blog.naver.com/PostView.nhn?blogId=popqser2&logNo=221229125022&parentCategoryNo=&categoryNo=23&viewDate=&isShowPopularPosts=true&from=search 
"""


# webdriver를 사용하기 위한 settings

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--disable-infobars")

class JbCrawling():
    keyword = ""
    mode = 1  # 1일 때에는 boxplot 구하는(목적 : 일일 게시물 개수) mode, 2일 때에는 검색된 게시물 개수(목적 : 최대 페이지 개수) 구하는 mode
    maxPageNum = 1
    pageNum = 1
    searchCount = 1
    outlier = 0
    absoluteUrl = []
    text = []
    month_list = []
    month_searchCount = []
    now = datetime.date.today().strftime("%Y.%m.%d")
    searchUrl =  "http://cafe984.daum.net/_c21_/cafesearch?grpid=aVeZ&fldid=&pagenum=" + str(pageNum) + "&listnum=20&item=subject&head=&query="+ keyword + "&attachfile_yn=&media_info=&viewtype=all&searchPeriod=" + now + "-" + now + "&sorttype=0&nickname="

    def __init__(self):
        # 변하지 않는 변수들은 init에 선언
        self.id = ''  # cafe id
        self.pw = ''  # cafe pw
        self.delay = 1  # time.sleep()에 쓰이는 delay(초)
        self.loginUrl = "https://logins.daum.net/accounts/loginform.do?url=http%3A%2F%2Fcafe984.daum.net%2F_c21_%2Fhome%3Fgrpid%3DaVeZ&category=cafe&t__nil_navi=login"

    def SettingDriver(self):
        print("Driver Setting 완료")
        self.driver = webdriver.Chrome('C:/Users/User/Desktop/chromedriver.exe')

    def SettingSession(self):
        print("Session Setting 완료")
        self.session = requests.Session()

    # 크롤링 첫 번째
    def InputKeyword(self, input):
        self.keyword = input
        self.GetSearchCount(input)
        return self.SearchAbsoluteUrl()

    def SearchAbsoluteUrl(self):
        print("=====JB Start=====")
        print("SearchAbsoluteUrl 함수 진입")
        self.GetMaxPageNum()
        for i in range(1, self.maxPageNum + 1):  # 1부터 maxPageNum까지
            self.pageNum = i
            self.searchUrl = "http://cafe984.daum.net/_c21_/cafesearch?grpid=aVeZ&fldid=&pagenum=" + str(i) + "&listnum=20&item=subject&head=&query="+ self.keyword + "&attachfile_yn=&media_info=&viewtype=all&searchPeriod=" + self.now + "-" + self.now + "&sorttype=0&nickname="
            response = self.session.get(self.searchUrl)
            urls = self.Scrape_List_Page(response)
            for url in urls:
                self.absoluteUrl.append(url)
        return self.Login()

    def GetSearchCount(self, keyword):
        self.SettingSession()
        self.searchUrl =  "http://cafe984.daum.net/_c21_/cafesearch?grpid=aVeZ&fldid=&pagenum=&listnum=20&item=subject&head=&query="+ keyword + "&attachfile_yn=&media_info=&viewtype=all&searchPeriod=" + self.now + "-" + self.now + "&sorttype=0&nickname="
        response = self.session.get(self.searchUrl)
        root = lxml.html.fromstring(response.content)
        root.make_links_absolute(response.url)
        for txt_point in root.cssselect('tbody > tr > td > div.search_result_box > em'):
            self.searchCount = int(txt_point.text)
        return self.searchCount

    def SearchPeriodMonth(self):
        print("    SearchPeriodMonth 함수 진입")
        now = datetime.date.today()
        oneMonthago = now - datetime.timedelta(days=31)
        for day in range(1, 31):
            month = oneMonthago + datetime.timedelta(days=day)
            month_str = month.strftime("%Y.%m.%d")
            self.month_list.append(month_str)

    def GetPeriodCount(self, keyword):
        self.SettingSession()
        print("GetPeriodeCount 함수 진입")
        self.SearchPeriodMonth()  # month_list를 작성
        print("       SearchPeriodMonth 함수 완료")
        for period in self.month_list:
            periodUrl = "http://cafe984.daum.net/_c21_/cafesearch?grpid=aVeZ&fldid=&pagenum=&listnum=20&item=subject&head=&query=" + keyword + "&attachfile_yn=&media_info=&viewtype=all&searchPeriod=" + period + "-" + period + "&sorttype=0&nickname="
            response = self.session.get(periodUrl)
            time.sleep(self.delay)
            root = lxml.html.fromstring(response.content)
            root.make_links_absolute(response.url)
            for txt_point in root.cssselect('tbody > tr > td > div.search_result_box > em'):
                self.month_searchCount.append(int(txt_point.text))

    def GetOutlier(self, keyword):
        self.GetPeriodCount(keyword)
        test1 = np.percentile(self.month_searchCount, 25)  # grades의 1사분위수 [ 하위 25% ]
        test2 = np.percentile(self.month_searchCount, 75)  # grades의 3사분위수 [ 하위 75% ]
        IQR = (test2 - test1)  # IQR은 사분위 범위(Q1 ~ Q3)
        self.outlier = test2 + IQR * 1.5  # test2 + IQR * 1.5  # 극단치 경계는 Q1(Q3) + 1.5 * IQR
        self.mode = 2  # Outlier 구하는 함수가 끝나면 mode를 2로 바꿔준다.
        return self.outlier

    def Scrape_List_Page(self, response):
        root = lxml.html.fromstring(response.content)
        root.make_links_absolute(response.url)
        for a in root.cssselect('tbody > tr > td.subject.searchpreview_subject > a'):
            if a == '#':
                continue
            url = a.get('href')
            # yield 구문으로 제너레이터의 요소 반환
            yield url

    def GetMaxPageNum(self):
        print("GetMaxPageNum 함수 진입")
        self.maxPageNum = int(self.searchCount / 20)  # 20은 목록 개수
        if self.searchCount % 20 != 0: self.maxPageNum += 1

    def Login(self):
        print("Login 함수 진입")
        self.SettingDriver()
        self.driver.get(self.loginUrl)
        time.sleep(self.delay)  # delay 초만큼 대기

        self.driver.find_element_by_id('id').send_keys(self.id)
        self.driver.find_element_by_id('inputPwd').send_keys(self.pw)
        self.driver.find_element_by_id('inputPwd').submit()
        time.sleep(self.delay)
        return self.SearchText()


    def SearchText(self):
        print("SearchText 함수 진입")
        for URL in self.absoluteUrl:
            self.driver.get(URL)
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            notices = soup.select('tbody > tr > td > p')

            for n in notices:
                buffer = n.text.strip()
                if buffer == "":
                    continue
                self.text.append(buffer)

            time.sleep(self.delay)
        self.driver.quit()

if __name__ == '__main__':
    print(DotaxCrawling().GetSearchCount())
