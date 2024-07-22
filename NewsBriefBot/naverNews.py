# 네이버 헤드라인 뉴스를 파싱하여 뉴스 객체를 생성합니다.
# 작성자: 양시현
# 수정 이력: 
# - 2024-02-04: 초기버전 생성
# - 2024-03-20: 콘솔 출력이 아닌 로그 파일로 기록하도록 수정

from urllib.parse import urljoin
from bs4 import BeautifulSoup # pip install beautifulsoup4
import requests # pip install requests requests
from datetime import datetime
import re
import threading
import queue
import logging
import os

from article import Article
import naverNewsDAO

class NaverNews:
    def __init__(self) -> None:
        self.logger = None
        # ConnectionError방지
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}
        self.dao = naverNewsDAO.NaverNewsDAO()
        
    def setup_logger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)


    def make_url(self) -> list:
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

    def articles_crawler(self, url):
        """
        주소에 존재하는 뉴스 링크들을 전부 가져온 후 배열로 반환
        """
        original_html = requests.get(url, headers=self.headers)
        html = BeautifulSoup(original_html.text, "html.parser")
        html = html.find('ul', class_='sa_list')
        links = html.find_all('a', class_='sa_text_title')
        temp = [link.get('href') for link in links]
        urls = []
        
        for i in temp:
            if not self.dao.is_url_exists(i):
                urls.append(i)
                # self.logger.info(f'{i}URL이 존재하지 않습니다.')
            # else:
                # self.logger.info(f'{i}URL이 존재합니다.')
                

        return urls


    def print_news(self, url, category) -> Article:
        """
        뉴스의 주소, 제목, 작성일, 본문, 신문사 반환
        """
        # 뉴스 html 크롤링
        original_html = requests.get(url, headers=self.headers)
        # 크롤링한 데이터의 본문
        html = BeautifulSoup(original_html.text, "html.parser")
        
        # 크롤링 데이터 저장
        # with open("output.html", "w", encoding="utf-8") as html_file:
        #     html_file.write(str(html))
        
        # 제목 파싱
        news_title = html.title.get_text(strip=True)
        
        # 날짜 파싱
        news_dates = html.find_all('div', class_='media_end_head_info_datestamp_bunch')
        date = None
        update_date = None
        if len(news_dates) == 2:
            date_text = news_dates[0].find('span').get_text(strip=True)
            update_date_text = news_dates[1].find('span').get_text(strip=True)

            update_date_parts = update_date_text.split(' ')
            update_time_str = update_date_parts[-1]  # 시간 부분
            if '오후' in date_text:
                u_hour, u_minute = map(int, update_time_str.split(':'))
                if u_hour != 12:  # 오후 12시는 그대로 유지
                    u_hour += 12
                update_time_str = f"{u_hour:02d}:{u_minute:02d}"
            # 시간 문자열을 datetime 객체로 변환
            update_date = datetime.strptime(f"{update_date_parts[0]} {update_time_str}", '%Y.%m.%d. %H:%M')
        else:
            # date_text = '작성일 ' + news_dates[0].find('span').get_text(strip=True)
            date_text = news_dates[0].find('span').get_text(strip=True)
        
        date_parts = date_text.split(' ')
        time_str = date_parts[-1]  # 시간 부분
        if '오후' in date_text:
            hour, minute = map(int, time_str.split(':'))
            if hour != 12:  # 오후 12시는 그대로 유지
                hour += 12
            time_str = f"{hour:02d}:{minute:02d}"
        # 시간 문자열을 datetime 객체로 변환
        date = datetime.strptime(f"{date_parts[0]} {time_str}", '%Y.%m.%d. %H:%M')
        

        # 신문사 파싱
        # 정규 표현식을 사용하여 office 객체 추출
        office_match = re.search(r'name\s*:\s*["\'](.*?)["\']', str(html))

        # 객체가 존재하는지 확인
        if office_match:
            office_json = str(office_match.group(1))
        else:
            office_json = ''

        # newspaper = html.select_one('.media_end_head_top_channel_layer_text strong').get_text(strip=True)

        # 기사 본문 파싱
        content = html.select_one('.newsct_article._article_body').get_text(strip=True)

        # 이미지 처리
        newsct_body = html.find('div', class_='newsct_article _article_body')
        img_tag = newsct_body.find('img')
        img_url = None

        # 이미지 존재 유무 처리
        if img_tag:
            img_url = img_tag['data-src']

        return Article(url, news_title, img_url, date, update_date, content, office_json, category)


    def start_crawling(self, global_task_queue: queue.Queue, queue_event: threading.Event):
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setup_logger("naverNews", os.path.join(log_dir, "naverNews.log"))  # Sub logger 설정
        self.logger = logging.getLogger("naverNews")
        self.logger.info('네이버 뉴스 크롤링 시작')

        category_urls = self.make_url()
        self.logger.debug('분야별 링크 생성 완료')
        self.dao.connect()
        for i in range(len(category_urls[0])):
            self.logger.debug(f'{category_urls[1][i]}파싱 시작')
            news_urls = self.articles_crawler(category_urls[0][i])
            for url in news_urls:
                # 뉴스 객체 반환
                news = self.print_news(url, category_urls[1][i])
                # 큐에 작업 추가
                global_task_queue.put(news)
                # 대기중인 브리핑 봇을 깨움
                queue_event.set()
        self.dao.disconnect()
        self.logger.info('네이버 뉴스 크롤링 완료')
