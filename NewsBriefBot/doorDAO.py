# Door 알림을 위한 DAO클래스
# 작성자: 양시현
# 수정 이력: 
# - 2024-03-23: 초기버전 생성

import mysql.connector
import os
import logging

class DoorDAO:
    def __init__(self, host="127.0.0.1", user="root", password="1234", database="capstone") -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.logger = None
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setup_logger("doorDAO", os.path.join(log_dir, "DoorDAO.log")) # logger 설정
        self.logger = logging.getLogger("system")

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

    def select_notify_users(self):
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT id, door_id, door_pw, name FROM UserInfo WHERE door_alert = True")
            door_announcement = cursor.fetchall()
            cursor.close()
            return door_announcement
        except mysql.connector.Error as err:
            self.logger.error(f"UserInfo 조회 오류: {err}")

    def select_door_announcement(self, id):
        try:
            cursor = self.conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT door_announcement_info FROM DoorAnnouncements WHERE id = %s", (id,))
            door_announcement = cursor.fetchone()
            cursor.close()
            return door_announcement
        except mysql.connector.Error as err:
            self.logger.error(f"{id} DoorAnnouncements 조회 오류: {err}")
        
    def insert_door_announcement(self, id, door_announcement_info):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO DoorAnnouncements (id, door_announcement_info) VALUES (%s, %s)",
                           (id, door_announcement_info))
            self.conn.commit()
            cursor.close()
            self.logger.debug("새로운 유저 정보가 추가되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"{id} DoorAnnouncements 삽입 오류: {err}")

    def update_door_announcement(self, id, door_announcement_info):
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE DoorAnnouncements SET door_announcement_info = %s WHERE id = %s",
                           (door_announcement_info, id))
            self.conn.commit()
            cursor.close()
            self.logger.debug("DoorAnnouncements 공지 알림 기록이 업데이트되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"DoorAnnouncements 업데이트 오류: {err}")

    def delete_door_announcement(self, id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM DoorAnnouncements WHERE id = %s", (id,))
            self.conn.commit()
            cursor.close()
            self.logger.debug(f"{id} Door 알림 유저 정보가 제거되었습니다.")
        except mysql.connector.Error as err:
            self.logger.error(f"DoorAnnouncements 삭제 오류: {err}")