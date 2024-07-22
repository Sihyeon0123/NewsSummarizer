# finviz map 이미지 파싱용
# 작성자: 양시현
# 수정 이력: 
# - 2024-04-06: 초기버전 생성

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import logging
import os

import finvizMapDAO

class FinvizMap:

    def __init__(self):
        self.driver = None       
        self.dao = finvizMapDAO.FinvizMapDAO()
        self.logger = None
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.6422.76"}
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setupLogger("FinvizMap", os.path.join(log_dir, "FinvizMap.log")) # logger 설정
        self.logger = logging.getLogger("FinvizMap")
        self.logger.info('FinvizMap 파싱시작')
        
    def setupLogger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)

    def runCrawling(self):
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
            # 웹 페이지로 이동
            mapUrl = "https://finviz.com/map.ashx?t=sec"
            self.driver.get(mapUrl)
        except TimeoutException:
            self.logger.error('로드시간이 너무 깁니다.')

        # 이미지 생성을 위한 버튼 클릭 후 대기
        try:
            mapButt = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div.border-finviz-blue-gray.bg-\[\#363a46\].text-\[\#94a3b8\].shadow.mb-0\.5.flex.h-10.items-center > div.flex.px-2 > button:nth-child(2)')))
            mapButt.click()
        except:
            self.logger.error("버튼 로딩에 실패하였습니다.")

        # 버튼을 클릭한 후 이미지가 로딩 될 때까지 대기
        try:
            img_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[@alt='S&P 500 Map']")))
            img_tag = img_element.get_attribute('outerHTML')
        except:
            self.logger.error("이미지 로딩에 실패하였습니다.")

        # DB에 저장
        self.dao.connect()  
        self.dao.insertNews(BeautifulSoup(img_tag, 'html.parser').img.get('src'))
        self.dao.disconnect()
        self.logger.info("S&P 500 Map 생성완료")
