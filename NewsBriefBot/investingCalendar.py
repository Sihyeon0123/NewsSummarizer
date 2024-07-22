# investingCalendar 실시간 뉴스 크롤링
# 작성자: 양시현
# 수정 이력: 
# - 2024-04-06: 초기버전 생성

from bs4 import BeautifulSoup # pip install beautifulsoup4
import requests # pip install requests requests
import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import investingDAO
import investingInfoBody

class InvestingCalendar:

    def __init__(self):
        self.dao = investingDAO.InvestingDAO()
        self.logger = None
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.6422.76 Safari/53.36"}
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setupLogger("InvestingCalendar", os.path.join(log_dir, "InvestingCalendar.log")) # logger 설정
        self.logger = logging.getLogger("InvestingCalendar")
        self.logger.info('InvestingCalendar 파싱시작')
        
    def setupLogger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)

    def runCrawling(self):
        self.logger.debug('이벤트 파싱 시작')
        url = 'https://kr.investing.com/economic-calendar/'

        # 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # headless 모드 설정
        chrome_options.add_argument("--log-level=3") # 로그 제거
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.headers}")
        # 크롬 브라우저를 실행하고 WebDriver 객체 생성
        if os.name == 'posix':  # 리눅스용
            self.logger.info('리눅스 환경입니다.')
            service = Service(executable_path='/home/deu-capstone/chrome/chromedriver-linux64/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        elif os.name == 'nt':  # 윈도우용
            self.logger.info('윈도우 환경입니다.')
            self.driver = webdriver.Chrome(options=chrome_options)

        try:
            self.driver.set_page_load_timeout(5)
            self.driver.get(url)
            page_source = self.driver.page_source
        except TimeoutException:
            page_source = self.driver.page_source

        # 페이지 소스 가져오기
        # page_source = self.driver.page_source
        # 페이지 가져오기
        # original_html = requests.get(url, headers=self.headers)
        # BeautifulSoup 객체로 변환
        # html = BeautifulSoup(original_html.text, "html.parser")
        html = BeautifulSoup(page_source, "html.parser")

        # with open("output.html", "w", encoding="utf-8") as file:
        #     file.write(html.prettify())

        # 테이블 가져오기
        table = html.find_all('tr', class_='js-event-item')
        
        eventList = []

        for i in table:
            tdList = i.find_all('td')
            # url
            url = 'https://kr.investing.com/'+tdList[3].find('a').get('href')
            # 시간
            date = datetime.strptime(i.get('data-event-datetime'), "%Y/%m/%d %H:%M:%S")
            # 나라
            country = i.span.get('title')
            # 중요성
            importance = i.find('td', class_='left textNum sentiment noWrap').get('data-img_key')[-1]
            # 이벤트 
            eventDescription =i.find('a').text.strip()
            # 실제
            actual = tdList[4].text
            # 예측
            forecast = tdList[5].text
            # 이전
            previous = tdList[6].text
            
            eventList.append(investingInfoBody.InvestingInfoBody(url, date, country, importance, eventDescription, forecast, actual, previous))
        
        self.logger.info('이벤트 크롤링 완료')

        self.dao.connect()
        for event in eventList:
            if not self.dao.isUrlExists(event.url):
                self.dao.insertEvent(event)
        self.dao.disconnect() 
