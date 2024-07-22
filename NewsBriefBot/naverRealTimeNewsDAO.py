# 네이버 실시간 뉴스 저장을 위한 DAO 
# 작성자: 양시현
# 수정 이력: 
# - 2024-04-06: 초기버전 생성

import mysql.connector
import os
import logging

from naverRealTimeNewsBody import NaverRealTimeNewsBody

class NaverRealTimeNewsDAO:
    def __init__(self, host="127.0.0.1", user="root", password="1234", database="capstone") -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.logger = None
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setupLogger("NaverRealTimeNewsDAO", os.path.join(log_dir, "NaverRealTimeNewsDAO.log")) # logger 설정
    
    def setupLogger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)
        
    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                user = self.user, 
                password = self.password, 
                host = self.host,
                database = self.database
            )
            self.logger.debug("MySQL DB에 연결되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"MySQL DB 연결 중 오류 발생:{err}")
            raise

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.logger.debug("MySQL DB와 연결이 해제되었습니다.")
        else:
            self.logger.warning("MySQL DB와 연결이 이미 닫혔습니다.")

    def selectNews(self):
        query = """
        SELECT title
        FROM NaverRealTimeNews
        WHERE DATE(created_at) BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 DAY) AND CURDATE()
        """
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query)
            door_announcement = cursor.fetchall()
            cursor.close()
            return door_announcement
        except mysql.connector.Error as err:
            self.logger.error(f"NaverRealTimeNews 뉴스 원본 조회 오류: {err}")
    
    def isUrlExists(self, url):
        query = """
        SELECT news_url 
        FROM NaverRealTimeNews
        WHERE news_url = %s;
        """
        args = (url,)  # 튜플로 전달하기 위해 괄호 추가
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, args)
            door_announcement = cursor.fetchall()
            cursor.close()
            return bool(door_announcement)  # 결과값이 있으면 True, 없으면 False 반환
        except mysql.connector.Error as err:
            self.logger.error(f"NaverRealTimeNews 주소 조회 오류: {err}")
            return False  # 에러가 발생한 경우에도 False 반환

    def insertNews(self, news:NaverRealTimeNewsBody):
        query = """
        INSERT INTO NaverRealTimeNews (title, news_url, image_url, publisher, created_at, category)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (news.title, news.url, news.img_url, news.newspaper, news.date, news.category))
            self.conn.commit()
            cursor.close()
            self.logger.debug(f"{news.url}: 새로운 실시간 뉴스가 추가되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"NaverRealTimeNews 삽입 오류: {err}")
        
    def deleteNews(self, id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM NaverRealTimeNews WHERE id = %s", (id,))
            self.conn.commit()
            cursor.close()
            self.logger.debug(f"{id} 제거되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"NaverRealTimeNews 삭제 오류: {err}")
        