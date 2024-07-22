# 네이버 실시간 뉴스를 파싱하여 DB에 저장합니다.
# 작성자: 양시현
# 수정 이력: 
# - 2024-04-06: 초기버전 생성

from urllib.parse import urljoin
from bs4 import BeautifulSoup # pip install beautifulsoup4
import requests # pip install requests requests
from datetime import datetime
import logging
import os

import naverRealTimeNewsDAO
import naverRealTimeNewsBody

class NaverRealTimeNews:
    def __init__(self) -> None:
        self.logger = None
        # ConnectionError방지
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}
        self.dao = naverRealTimeNewsDAO.NaverRealTimeNewsDAO()
        
    def setupLogger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)
        
    def makeUrl(self) -> list:
        """
        네이버 뉴스의 카테고리는 
        정치, 경제, 사회 생활/문화, IT/과학, 세계 6개로 나뉜 후 
        세부 항목으로 나뉜다
        """
        # # 검색할 날짜 20240101 형식
        # temp_date = datetime.now()
        # 정치 경제 사회 생활/문화 IT/과학 세계
        category = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학"]
        category_num = [100, 101, 102, 103, 104, 105]
        urls = []
        news_category_urls = []
        for i in category_num:
            urls.append("https://news.naver.com/section/" + str(i))

        news_category_urls.append(urls)
        news_category_urls.append(category)
        return news_category_urls

    def getDate(self, url) -> datetime:
        """
            뉴스의 작성일 정보 반환
        """
        original_html = requests.get(url, headers=self.headers)
        # 크롤링한 데이터의 본문
        html = BeautifulSoup(original_html.text, "html.parser")
        selectedDate = html.select('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span')
        # 크롤링 데이터 저장 - debug
        # with open("output2.html", "w", encoding="utf-8") as html_file:
        #     html_file.write(str(selectedDate))
        return datetime.strptime(selectedDate[0].get('data-date-time'), "%Y-%m-%d %H:%M:%S")

    def realTimeNewsCrawler(self, url, category):
        """
        주소에 존재하는 뉴스 링크들을 전부 가져온 후 배열로 반환
        """
        original_html = requests.get(url, headers=self.headers)
        html = BeautifulSoup(original_html.text, "html.parser")

        # 실시간 뉴스 목록을 가져온다    
        selectedHtml = html.select('#newsct > div.section_latest > div > div.section_latest_article._CONTENT_LIST._PERSIST_META')
        divs = selectedHtml[0].find_all('li', class_='sa_item _LAZY_LOADING_WRAP')
        
        # with open("output.html", "w", encoding="utf-8") as html_file:
        #     html_file.write(str(divs))
        
        # 실시간 뉴스의 주소를 가져와 배열로 저장
        urls = [div.a.get('href') for div in divs]
        titles = [div.strong.get_text() for div in divs]
        publishers = [div.find('div', class_='sa_text_press').get_text() for div in divs]
        imgURLs =  [div.img.get('data-src') for div in divs]

        realTimeNewsList = []

        # DB에 저장된 URL인지 판단 후 저장되어 있다면 무시하고 없다면 저장
        for i in range(len(urls)):
            if not self.dao.isUrlExists(urls[i]):
                # self.logger.info(f'{urls[i]}URL이 존재하지 않습니다.')
                date = self.getDate(urls[i])
                realTimeNewsList.append(naverRealTimeNewsBody.NaverRealTimeNewsBody(urls[i], titles[i], imgURLs[i], date, publishers[i], category))
            # else:
            #     self.logger.info(f'{urls[i]}URL이 존재합니다.')

        return realTimeNewsList

    def startCrawling(self):
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setupLogger("naverRealTimeNews", os.path.join(log_dir, "naverRealTimeNews.log"))  # Sub logger 설정
        self.logger = logging.getLogger("naverRealTimeNews")
        self.logger.info('네이버 실시간 뉴스 크롤링 시작')

        category_urls = self.makeUrl()
        self.logger.debug('링크 생성 완료')
        
        self.dao.connect()
        # 실시간 뉴스 파싱 시작
        for i in range(len(category_urls[0])):
            self.logger.debug(f'{category_urls[1][i]}의 실시간 뉴스 파싱 시작')
            newsList = self.realTimeNewsCrawler(category_urls[0][i], category_urls[1][i])
            for news in newsList:
                self.dao.insertNews(news)

        self.dao.disconnect()
        self.logger.info('네이버 실시간 뉴스 크롤러 대기전환')


if __name__ == "__main__":
    a = NaverRealTimeNews()
    a.startCrawling()