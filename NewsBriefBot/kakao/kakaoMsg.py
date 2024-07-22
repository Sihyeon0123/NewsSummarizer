# 카카오톡으로 알림을 보내기 위한 클래스입니다.
# 작성자: 양시현
# 수정 이력: 
# - 2024-03-19: 초기버전 생성

# rest key: 11aa535784ec16106ad1f8e387d551ff
# authorize code를 받아오기 위한 주소로 알림을 받기 위해서는 접속이 필요
# https://kauth.kakao.com/oauth/authorize?client_id=11aa535784ec16106ad1f8e387d551ff&redirect_uri=https://example.com/oauth&response_type=code&scope=talk_message,friends
# authorize code: 8-nuN1BF1s99gI7Wtqp5If4TVtrHhZVi-TwS_GKIChCFodAbmNvXgIfhCLgKPXTZAAABjlbSGaQhI_W2iNNaeg
import requests
import json
import os
import logging

class KakaoMsg:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
            cls._instance.setup_logger("kakao", os.path.join(log_dir, "kakaoMsg.log")) # logger 설정
            cls._instance.logger = logging.getLogger("kakao")
            cls._instance.logger.info('카카오 객체 생성')
            cls.rest_api_key = '11aa535784ec16106ad1f8e387d551ff'
            cls.redirect_uri = 'https://example.com/oauth'
            cls.tokenUrl = "https://kauth.kakao.com/oauth/token"
        return cls._instance
    
    def setup_logger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)

    def refresh(self, existing_token:json):
        kakao_path = os.path.dirname(__file__)
        files_path = os.path.join(kakao_path, "files")
        root_token_path = os.path.join(files_path, "root_token.json")
        data = {
            "grant_type": "refresh_token",
            "client_id": self.rest_api_key,
            "refresh_token": existing_token['refresh_token']
        }
        response = requests.post(self.tokenUrl, data=data)
        new_token = response.json()
        existing_token['access_token'] = new_token['access_token']

        # kakao_code.json 파일 저장
        with open(root_token_path, "w") as fp:
            json.dump(existing_token, fp)

        return existing_token

    def getFriendList(self, tokens:json) -> json:
        # 친구목록을 요청하기 위한 headers 및 params
        url = "https://kapi.kakao.com/v1/api/talk/friends"
        access_token = tokens['access_token']
        params = {"limit": 10}
        headers = {"Authorization": "Bearer " + access_token}

        response = requests.get(url, headers=headers, params=params)

        return response.json()

    def main(self):
        kakao_path = os.path.dirname(__file__)
        files_path = os.path.join(kakao_path, "files")
        root_token_path = os.path.join(files_path, "root_token.json")
        friend_list_path = os.path.join(files_path, "friend_list.json")
        authorize_code = '8-nuN1BF1s99gI7Wtqp5If4TVtrHhZVi-TwS_GKIChCFodAbmNvXgIfhCLgKPXTZAAABjlbSGaQhI_W2iNNaeg'
        # 파일이 존재한다면 
        if os.path.exists(root_token_path):
            self.logger.info("토큰이 존재함으로 기존의 데이터로 진행합니다")
            with open(root_token_path, "r") as fp:
                tokens = json.load(fp)
        # 파일이 없다면 수행
        else:
            self.logger.warning("토큰파일을 찾을 수 없어 새로운 값 대기중")
            print("주소에 접속 후 code= 뒤의 문자열을 입력해 주세요")
            print("https://kauth.kakao.com/oauth/authorize?client_id=11aa535784ec16106ad1f8e387d551ff&redirect_uri=https://example.com/oauth&response_type=code&scope=talk_message,friends")
            authorize_code = input()
            self.logger.warning("새로운 값 입력 완료")
            # 요청 데이터 생성
            data = {
                'grant_type':'authorization_code',
                'client_id':self.rest_api_key,
                'redirect_uri':self.redirect_uri,
                'code': authorize_code,
            }

            # 요청을 보낸 후 결과를 변수에 저장
            response = requests.post(self.tokenUrl, data=data)
            # json으로 변환 후 출력
            tokens = response.json()

            # json 저장
            with open(root_token_path,"w") as fp:
                json.dump(tokens, fp)

        # JSON 형태로 변환
        friend_list = self.getFriendList(tokens)

        try:
            friend_list['code']
            self.logger.warning("main: access_token을 다시 받아와야함\n")
            self.refresh(tokens)
            friend_list = self.getFriendList(tokens)
        except KeyError:
            self.logger.info("main: access_token 유효")

        with open(friend_list_path, 'w') as fp:
            json.dump(friend_list, fp)

        return tokens, friend_list
    
    def sendMsgToMe(self, msg):
        authorize_code = 'daqwkbYMRYODWpasSIKV9ScYkhuQFijIsioQZx0elBcz5phS5VH96JUHHzkKPXKYAAABjmfb77mt1856Xp2T3g'
        kakao_path = os.path.dirname(__file__)
        files_path = os.path.join(kakao_path, "files")
        my_token_path = os.path.join(files_path, "my_token.json")
        send_url="https://kapi.kakao.com/v2/api/talk/memo/default/send"

        data={
            "template_object": json.dumps({
                "object_type":"text",
                "text":msg,
                "link":{
                    "web_url":"www.naver.com"
                }
            })
        }
        
        if os.path.exists(my_token_path):
            self.logger.info("기존의 데이터로 수행")
            with open(my_token_path, "r") as fp:
                tokens = json.load(fp)
        # 파일이 없다면 수행
        else:
            self.logger.warning("정보가 존재하지 않습니다.")
            print("주소에 접속 후 code= 뒤의 문자열을 입력해 주세요")
            print("https://kauth.kakao.com/oauth/authorize?client_id=11aa535784ec16106ad1f8e387d551ff&redirect_uri=https://example.com/oauth&response_type=code&scope=talk_message,friends")
            authorize_code = input()
            # access_token, 등을 받다오기 위한 주소
            # 요청 데이터 생성
            data3 = {
                'grant_type':'authorization_code',
                'client_id':self.rest_api_key,
                'redirect_uri':self.redirect_uri,
                'code': authorize_code,
            }
            response = requests.post(self.tokenUrl, data=data3)
            tokens = response.json()
            # json 저장
            with open(my_token_path,"w") as fp:
                json.dump(tokens, fp)

        send_headers={
            "Authorization" : "Bearer " + tokens["access_token"]
        }
        response = requests.post(send_url, headers=send_headers, data=data)
        if response.status_code == 401:
            self.logger.warning("me: access_token을 다시 받아와야함\n")
            data2 = {
                "grant_type": "refresh_token",
                "client_id": self.rest_api_key,
                "refresh_token": tokens['refresh_token']
            }
            response = requests.post(self.tokenUrl, data=data2)
            new_token = response.json()
            tokens['access_token'] = new_token['access_token']
            # kakao_code.json 파일 저장
            with open(my_token_path, "w") as fp:
                json.dump(tokens, fp)
            
            send_headers={
                "Authorization" : "Bearer " + tokens["access_token"]
            }
            requests.post(send_url, headers=send_headers, data=data)

    def sendMsg(self, msg:str, uuid:str, access_token:str):
        # 헤더 생성
        headers={"Authorization" : "Bearer " + access_token}
        # 전송할 url
        send_url= "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
        # 전송할 데이터
        data={
            'receiver_uuids': '["{}"]'.format(uuid),
            "template_object": json.dumps({
                "object_type":"text",
                "text":msg,
                "link":{
                    "web_url":"http://door.deu.ac.kr/",
                },
                "button_title": "확인"
            })
        }

        # 전송
        response = requests.post(send_url, headers=headers, data=data)
        # 코드
        return response.status_code
    
    def sendMessageToKakao(self, msg="", name=""):
        self.logger.info(f"{name}에게 메시지 전송 준비")
        if name == "양시현":
            self.sendMsgToMe(msg)
            return
        
        token, friend_list = self.main() # 메세지를 전송할 준비
        found = False
        
        # 친구 목록에서 이름을 찾아 그 사람의 uuid를 전송
        for element in friend_list['elements']:
            if element['profile_nickname'] == name:
                code = self.sendMsg(msg, element['uuid'], token['access_token'])
                found = True
                if code == 200:
                    self.logger.info(f"code 200: {name}에게 메시지 전송 완료")
                    break
                elif code == 400:
                    self.logger.error(f"code 400: {name}에게 메시지 전송 실패")
                    break

        if not found:
            # 해당 이름을 찾지 못한 경우 실행할 코드
            self.logger.error(f"{name}을 찾을 수 없습니다.")

    