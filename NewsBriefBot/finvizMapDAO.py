# S&P 500 MAP 저장을 위한 DAO 
# 작성자: 양시현
# 수정 이력: 
# - 2024-03-23: 초기버전 생성

import mysql.connector
import os
import logging

import article

class FinvizMapDAO:
    def __init__(self, host="127.0.0.1", user="root", password="1234", database="capstone") -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.logger = None
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setup_logger("FinvizMapDAO", os.path.join(log_dir, "FinvizMapDAO.log")) # logger 설정
    
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

    def selectNews(self):
        query = """
        SELECT url 
        FROM FinvizMap 
        WHERE DATE(created_at) BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 DAY) AND CURDATE()
        """
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query)
            door_announcement = cursor.fetchall()
            cursor.close()
            return door_announcement
        except mysql.connector.Error as err:
            self.logger.error(f"FinvizMap  뉴스 원본 조회 오류: {err}")
    
    def insertNews(self, url):
        query = """
        INSERT INTO FinvizMap (url)
        VALUES (%s)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (url,))
            self.conn.commit()
            cursor.close()
            self.logger.debug("새로운 S&P 500 Map이 추가되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"FinvizMap 삽입 오류: {err}")
        
    def deleteMap(self, id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM FinvizMap  WHERE id = %s", (id,))
            self.conn.commit()
            cursor.close()
            self.logger.debug(f"{id} 제거되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"FinvizMap 삭제 오류: {err}")
        