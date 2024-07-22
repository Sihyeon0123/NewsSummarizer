# 뉴스 저장을 위한 DAO 
# 작성자: 양시현
# 수정 이력: 
# - 2024-05-05: 초기버전 생성

import mysql.connector
import os
import logging

import financialjuiceBody

class FinancialjuiceDAO:
    def __init__(self, host="127.0.0.1", user="root", password="1234", database="capstone") -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.logger = None
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setup_logger("FinancialjuiceDAO", os.path.join(log_dir, "FinancialjuiceDAO.log")) # logger 설정
    
    def setup_logger(self, name, log_file, level=logging.INFO):
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

    def isNewsExists(self, news:financialjuiceBody.FinancialjuiceBody):
        query = """
        SELECT event_description 
        FROM FinancialjuiceEvents
        WHERE event_time = %s;
        """
        args = (news.date,)  # 튜플로 전달하기 위해 괄호 추가
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, args)
            door_announcement = cursor.fetchall()
            cursor.close()
            return bool(door_announcement)  # 결과값이 있으면 True, 없으면 False 반환
        except mysql.connector.Error as err:
            self.logger.error(f"isNewsExists 주소 조회 오류: {err}")
            return False  # 에러가 발생한 경우에도 False 반환

    def insertNews(self, news:financialjuiceBody.FinancialjuiceBody):
        query = """
        INSERT INTO FinancialjuiceEvents (url, event_time, event_description)
        VALUES (%s, %s, %s)
        """
        if news.link is None:
            args = (None, news.date, news.news)
        else:
            args = (news.link, news.date, news.news)
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            self.conn.commit()
            cursor.close()
            self.logger.debug("Financialjuice: 새로운 뉴스가 추가되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"Financialjuice 삽입 오류: {err}")
  