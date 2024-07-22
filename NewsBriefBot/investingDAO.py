# 실시간 이벤트 저장을 위한 DAO 
# 작성자: 양시현
# 수정 이력: 
# - 2024-03-23: 초기버전 생성

import mysql.connector
import os
import logging

from investingInfoBody import InvestingInfoBody

class InvestingDAO:
    def __init__(self, host="127.0.0.1", user="root", password="1234", database="capstone") -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.logger = None
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setupLogger("InvestingDAO", os.path.join(log_dir, "InvestingDAO.log")) # logger 설정
    
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

    def selectEvent(self):
        query = """
        SELECT event_description 
        FROM InvestingRealTimeEvents 
        WHERE DATE(event_time) BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 DAY) AND CURDATE()
        """
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query)
            door_announcement = cursor.fetchall()
            cursor.close()
            return door_announcement
        except mysql.connector.Error as err:
            self.logger.error(f"FinvizMap  뉴스 원본 조회 오류: {err}")
    
    def isUrlExists(self, url):
        query = """
        SELECT url 
        FROM InvestingRealTimeEvents
        WHERE url = %s;
        """
        args = (url,)  # 튜플로 전달하기 위해 괄호 추가
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, args)
            door_announcement = cursor.fetchall()
            cursor.close()
            return bool(door_announcement)  # 결과값이 있으면 True, 없으면 False 반환
        except mysql.connector.Error as err:
            self.logger.error(f"InvestingRealTimeEvents 주소 조회 오류: {err}")
            return False  # 에러가 발생한 경우에도 False 반환
        
    def insertEvent(self, event:InvestingInfoBody):
        query = """
        INSERT INTO InvestingRealTimeEvents (url, event_time, country, importance, event_description, actual, forecast, previous)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (event.url, event.date, event.country, event.importance, event.eventDescription, event.actual, event.forecast, event.previous))
            self.conn.commit()
            cursor.close()
            self.logger.debug("새로운 Event가 추가되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"InvestingRealTimeEvents 삽입 오류: {err}")
        
    def deleteEvent(self, id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM InvestingRealTimeEvents WHERE id = %s", (id,))
            self.conn.commit()
            cursor.close()
            self.logger.debug(f"{id} 제거되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"InvestingRealTimeEvents 삭제 오류: {err}")
        