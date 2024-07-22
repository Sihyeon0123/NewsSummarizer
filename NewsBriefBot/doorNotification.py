# 동의대 계정을 이용하여 Door의 새로운 공지를 확인합니다!
# 계정 로그인, 강의 개수 확인, 각 공지 순회 후 개수 및 제목 파싱, 
# 로그인 실패 예외처리, 비밀번호 파일 읽기 예외처리
# 작성자: 양시현
# 수정 이력: 
# - 2024-03-17: 초기버전 생성
# - 2024-03-18: 코드 최적화, 강의 공지 번호를 가져오도록 수정
# - 2024-03-20: 아무 공지가 없더라도 강의명은 출력되도록 수정
# - 2024-03-20: 콘솔 출력이 아닌 로그 파일로 기록하도록 수정
# - 2024-03-22: 클래스로 변경, json처리 함수 추가

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
import json
import os

import doorDAO
import logging
import kakao.kakaoMsg

class DoorNotification:

    def __init__(self):
        self.driver = None       
        self.logger = None 
        self.dao = None
        self.kakao = kakao.kakaoMsg.KakaoMsg()
        
    def setup_logger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)


    # 전달받은 url의 강의실 메뉴와 강의실 번호를 조합하여 방문하며 col_index위치의 제목을 반환한다.
    # url: 방문할 메뉴, lecture_room_number: 강의실 번호, col_index: 제목의 위치
    def table_parsing(self, url:str, lecture_room_number:int, col_index:int) -> list:
        # 주소와 강의실번호를 조합하여 방문
        self.driver.get(url + str(lecture_room_number))

        # 방문한 페이지의 html을 가져온다
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # 클래스가 'tbl_type'인 테이블 요소 찾기
        table = soup.find('table', class_='tbl_type')
        
        # 테이블의 번호와 제목을 저장할 리스트
        table_items = []
        # 테이블 속의 공지 제목을 저장할 리스트
        table_title = []
        # 테이블 속의 공지 번호를 저장할 리스트 
        table_numbers = []

        # 테이블의 행을 가져온다
        table_rows = table.find_all('tr')
        # 테이블의 첫 행은 항목이기 때문에 무시
        if len(table_rows) > 1:
            # 테이블의 열을 가져온다
            table_cols = table_rows[1].find_all('td')
            # 테이블의 열이 1개 이상이라면
            if len(table_cols) > 1:
                # 테이블의 각 행별로 반복
                for row in table_rows[1:]:
                    # 테이블의 각 행의 제목을 파싱
                    table_name = row.find_all('td')[col_index].text.strip()  # 공지 제목 위치
                    table_number = row.find_all('td')[0].text.strip()  # 공지 번호
                    table_title.append(table_name)
                    table_numbers.append(table_number)

        # 파싱한 결과를 반환
        table_items.append(table_title)
        table_items.append(table_numbers)
        return table_items
    
    def get_json(self, id):
        data = self.dao.select_door_announcement(id)

        if data == None:
            return None
        elif data["door_announcement_info"]:
            return json.loads(data['door_announcement_info'])
        else:
            return None


    # 유저의 정보가 아예 없는경우 json생성
    def make_json(self, semester:str, lecture_names:list, id) -> dict:
        # 강의학기, 강의 이름 목록
        # 학기 항목 추가
        data = {
            semester:{}
        }
        
        for lecture in lecture_names:
            temp = {
                lecture:{
                    "과제": 0,
                    "수업활동일지": 0,
                    "팀프로젝트 결과": 0,
                    "공지사항": 0,
                    "강의자료": 0,
                    "알림": 0
                }
            }
            data[semester].update(temp)
        self.dao.insert_door_announcement(id, json.dumps(data))
        return data

    # 파싱 데이터와 json데이터를 비교하여 달라진게 있으면 알림을 보냄
    def compare_and_notify_changes(self, lecture_notice_list:list, semester:str, lecture:str, menu:str, name:str, json_data:dict):
        if len(lecture_notice_list[0]) == 0:
            return json_data
        
        if menu == "과제":
            # 파싱한 공지의 개수 - 알림을 보내 공지 개수
            new_notify_count = len(lecture_notice_list[0]) - json_data[semester][lecture][menu]
            for i in range(1, new_notify_count + 1):
                # 알림 처리로직 추가
                self.kakao.sendMessageToKakao(f"{lecture}({menu}): \"{lecture_notice_list[0][-i]}\"가 공지되었습니다.", name)
                json_data[semester][lecture][menu] += 1
        elif menu == "공지":
            # 공지에는 공지번호 말고도 "알림"이라는 것이 존재하기 때문에 따로 처리가 필요하다
            alarm_count = 0
            # "알림" 처리
            for i in lecture_notice_list[1]:
                if i == "알림":
                    alarm_count += 1
            # 보내지 않은 "알림"공지를 보낸다
            if alarm_count > json_data[semester][lecture]["알림"]:
                for i in range(alarm_count - json_data[semester][lecture]["알림"]):
                    # 알림 처리로직 추가
                    self.kakao.sendMessageToKakao(f"{lecture}({menu}): \"{lecture_notice_list[0][-i]}\"가 공지되었습니다.", name)
                    json_data[semester][lecture]["알림"] += 1
            
            # 보내지 않은 공지를 보낸다
            notify_count = lecture_notice_list[1][alarm_count] - json_data[semester][lecture][menu]
            if notify_count > 0:
                for i in range(alarm_count, alarm_count + notify_count):
                    # 알림 처리로직 추가
                    self.kakao.sendMessageToKakao(f"{lecture}({menu}): \"{lecture_notice_list[0][-i]}\"가 공지되었습니다.", name)
                    json_data[semester][lecture][menu] += 1

        else:
            # 10이 넘어가는 경우 예외 처리
            new_notify_count = int(lecture_notice_list[1][0]) - json_data[semester][lecture][menu]

            if new_notify_count > 10:
                new_notify_count = 10
                json_data[semester][lecture][menu] += int(lecture_notice_list[1][0]) - 10

            if new_notify_count > 0:
                for i in range(new_notify_count):
                    # 알림 처리로직 추가
                    self.kakao.sendMessageToKakao(f"{lecture}({menu}): \"{lecture_notice_list[0][i]}\"가 공지되었습니다.", name)
                    json_data[semester][lecture][menu] += 1
    
        return json_data
        


    def run_door_crawling(self, id, door_id, door_pw, name):
        
        # 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # headless 모드 설정
        chrome_options.add_argument("--log-level=3") # 로그 제거
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # 크롬 브라우저를 실행하고 WebDriver 객체 생성
        if os.name == 'posix':  # 리눅스용
            self.logger.info('리눅스 환경입니다.')
            service = Service(executable_path='/home/deu-capstone/chrome/chromedriver-linux64/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        elif os.name == 'nt':  # 윈도우용
            self.logger.info('윈도우 환경입니다.')
            self.driver = webdriver.Chrome(options=chrome_options)

        # 웹 페이지로 이동
        login_url = "https://door.deu.ac.kr/sso/login.aspx"
        self.driver.get(login_url)

        # 아이디 입력
        id_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[2]/div[1]/div/table/tbody/tr[1]/td[2]/input')))
        id_input.send_keys(door_id)

        # 비밀번호 입력
        pw_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[2]/div[1]/div/table/tbody/tr[2]/td/input')))
        pw_input.send_keys(door_pw)

        try:
            # 로그인 버튼 클릭
            login_button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[2]/div[1]/div/table/tbody/tr[1]/td[3]/a')))
            login_button.click()
            
        except TimeoutException:
            self.logger.error(f'{name}: 로그인 버튼을 찾을 수 없거나 클릭할 수 없습니다.')
            return
        except Exception as e:
            self.logger.error(f'{name}: 로그인 도중 오류가 발생했습니다:', e)
            return
        
        self.logger.debug(f'{name}: 로그인 완료')

        try:
            # 강의실로 이동
            self.driver.get('http://door.deu.ac.kr/MyPage')
            self.logger.debug(f'{name}: 강의 목록 파싱')

            # 강의 목록을 가져옴
            lecture_list_selector = "#wrap > div.subpageCon > div:nth-child(3) > div:nth-child(3) > table"
            lecture_list = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, lecture_list_selector)))

            # lecture_list를 BeautifulSoup으로 파싱
            soup = BeautifulSoup(lecture_list.get_attribute('outerHTML'), 'html.parser')

            # 강의 목록에서 강의 이름 추출
            lecture_names = []
            lecture_room_numbers = []
            lecture_count = 0
            semester = None

            # 강의 목록이 비어있는 경우에 대한 예외 처리
            lecture_rows = soup.find_all('tr')
            if len(lecture_rows) > 1:  # 강의 목록에 최소 두 개의 행이 존재하는 경우
                # 강의 학기
                semester = lecture_rows[1].find_all('td')[0].text.strip() # 강의 학기
                for row in lecture_rows[1:]:  # 첫 번째 행은 헤더이므로 무시
                    room_number = row.find('a')['href'].split("'")[1]
                    lecture_room_numbers.append(room_number)
                    lecture_name = row.find_all('td')[2].text.strip()  # 세 번째 열이 강의 이름
                    lecture_names.append(lecture_name)
                lecture_count = len(lecture_names)
            else:
                self.logger.warning(f'{name}: 강의목록이 비어있습니다.')
                return

            # json 관련 처리
            json_data = self.get_json(id)
            
            # DB에서 json을 받아와 처리
            # json데이터가 존재하는지 확인
            if json_data:
                self.logger.debug(f'{name}: 공지 json파일이 존재')
                # json_data에 이번 학기 정보가 존재하는지 확인
                if not semester in json_data:
                    self.logger.debug(f'{name}: 의 학기 정보를 새로 만드는 중')
                    json_data = self.make_json(semester, lecture_names)
            else:
                self.logger.debug(f'{name}: 의 학기 Json을 새로 만드는 중')
                json_data = self.make_json(semester, lecture_names, id)
            
            # 크롤링할 주소와 그 주소에 존재하는 테이블의 제목 위치
            urls = [
                ["http://door.deu.ac.kr/LMS/LectureRoom/CourseHomeworkStudentList/", 2, "과제"],
                ["http://door.deu.ac.kr/LMS/LectureRoom/CourseOutputs/", 1, "수업활동일지"],
                ["http://door.deu.ac.kr/LMS/LectureRoom/CourseTeamProjectStudentList/", 1, "팀프로젝트 결과"],
                ["http://door.deu.ac.kr/BBS/Board/List/CourseNotice?cNo=", 2, "공지사항"],
                ["http://door.deu.ac.kr/BBS/Board/List/CourseReference?cNo=", 2, "강의자료"]
            ]

            self.logger.debug(f'{name}: 공지 파싱 시작')
            # 새로운 공지 확인 시작
            for i in range(lecture_count):
                # 강의실 1개 마다 urls에 들어있는 모든 링크를 방문한다
                for url in urls:
                    # 메뉴 이름 저장
                    menu = url[2]
                    # 강의실에서 방문할 링크, 강의실 번호, 제목의 위치를 보내 파싱한다.
                    lecture_notice_list = self.table_parsing(url[0], lecture_room_numbers[i], url[1])
                    json_data = self.compare_and_notify_changes(lecture_notice_list, semester, lecture_names[i], menu, name, json_data)

            self.logger.debug(f'{name}: 공지 파싱 종료')
        except TimeoutException:
            self.logger.error("요소를 찾을 수 없거나 연결 시간이 초과되었습니다.")
            return 
        except Exception as e:
            self.logger.error("오류가 발생했습니다:%s", e)
            return 
        
        self.dao.update_door_announcement(id, json.dumps(json_data))

    def start(self):
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setup_logger("doorNotification", os.path.join(log_dir, "doorNotification.log")) # logger 설정
        self.logger = logging.getLogger("doorNotification")
        self.logger.debug('도어 크롤링 시작')

        self.dao = doorDAO.DoorDAO()
        self.dao.connect()
        users = self.dao.select_notify_users()

        if users:
            for i in users:
                self.run_door_crawling(i["id"], i["door_id"], i["door_pw"], i["name"])
        else:
            self.logger.debug("도어 알림을 신청한 유저가 없습니다.")
        self.dao.disconnect()
        self.logger.info('도어 크롤링 종료')
        

if __name__ == "__main__":
    a = DoorNotification()
    a.run_door_crawling()
    