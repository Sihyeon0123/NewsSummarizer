# financialjuice 실시간 뉴스 크롤링
# 작성자: 양시현
# 수정 이력: 
# - 2024-05-05: 초기버전 생성

from bs4 import BeautifulSoup # pip install beautifulsoup4
import logging
import os
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import financialjuiceBody
import financialjuiceDAO

class Financialjuice:
    def __init__(self):
        self.logger = None
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.6422.76"}
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setupLogger("Financialjuice", os.path.join(log_dir, "Financialjuice.log")) # logger 설정
        self.logger = logging.getLogger("Financialjuice")

        self.dao = financialjuiceDAO.FinancialjuiceDAO()

        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # headless 모드 설정
        self.chrome_options.add_argument("--log-level=3") # 로그 제거
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument(f"user-agent={self.headers}")
        # self.chrome_options.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102")
        
    def setupLogger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)

    def runCrawling(self):
        self.logger.debug('Financialjuice 파싱시작')
        url = 'https://www.financialjuice.com/home'
        # 크롬 브라우저를 실행하고 WebDriver 객체 생성
        if os.name == 'posix':  # 리눅스용
            self.logger.info('리눅스 환경입니다.')
            service = Service(executable_path='/home/deu-capstone/chrome/chromedriver-linux64/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        elif os.name == 'nt':  # 윈도우용
            self.logger.info('윈도우 환경입니다.')
            self.driver = webdriver.Chrome(options=self.chrome_options)

        # 웹 페이지로 이동
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 180)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "headline-title")))
            
        # with open("output.html", "w", encoding="utf-8") as html_file:
        #      html_file.write(str(driver.page_source))

        # BeautifulSoup 객체로 변환
        html = BeautifulSoup(self.driver.page_source, "html.parser")
        # div 가져오기
        div = html.find('div', id='mainFeed', attrs={'data-feedid': 'mainfeed'})
        divs = div.find_all('div', class_='col-xs-12 infinite-item headline-item')
        
        newsList = []
        for div_item in divs:
            temp = financialjuiceBody.FinancialjuiceBody()
            spans = div_item.find_all('span', class_='headline-title-nolink')            
            # 만약 비지 않았다면
            if spans:
                temp.news = spans[0].text.strip()
                # print(spans[0].text.strip())
            else:
                a = div_item.find_all('a', href=lambda href: href and 'https://www.financialjuice.com/' in href)
                if a:
                    if a[0].text.strip() != "Save 92% on an annual subscription using Promo code JUICY92":
                        temp.news = a[0].text.strip()
                        temp.link = a[0].get('href')
                        # print(a[0].text.strip())
                        # print(a[0].get('href'))

            p = div_item.find_all('p', class_='time')
            if p:
                if p[0].text.strip() != "Don't like Ads? GO PRO":
                    date_str = p[0].text.strip()
                    # 현재 연도 가져오기
                    current_year = datetime.now().year
                    # 날짜 문자열을 datetime 객체로 변환
                    temp.date = datetime.strptime(date_str + f" {current_year}", "%H:%M %b %d %Y")
                    # print(date_obj.strftime("%Y-%m-%d %H:%M"))
            newsList.append(temp)

        # None 객체 제거
        newsList = [a for a in newsList if a.news is not None]

        # for a in newsList:
        #     print(a.news, a.date, a.link)
        self.logger.info('Financialjuice 크롤링 완료')

        self.dao.connect()
        for news in newsList:
            if not self.dao.isNewsExists(news):
                self.dao.insertNews(news)
        self.dao.disconnect() 
