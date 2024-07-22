# rest key: 11aa535784ec16106ad1f8e387d551ff
# authorize code를 받아오기 위한 주소로 알림을 받기 위해서는 접속이 필요
# https://kauth.kakao.com/oauth/authorize?client_id=11aa535784ec16106ad1f8e387d551ff&redirect_uri=https://example.com/oauth&response_type=code&scope=talk_message,friends

import requests
import json
import os

class AddFriend:
    def __init__(self) -> None:
        pass

    def getFriendList(self, tokens:json) -> json:
        # 친구목록을 요청하기 위한 headers 및 params
        url = "https://kapi.kakao.com/v1/api/talk/friends"
        access_token = tokens['access_token']
        params = {"limit": 10}
        headers = {"Authorization": "Bearer " + access_token}

        response = requests.get(url, headers=headers, params=params)

        return response.json()


    def main(self, ):
        print("주소에 접속 후 code= 뒤의 문자열을 입력해 주세요")
        print("https://kauth.kakao.com/oauth/authorize?client_id=11aa535784ec16106ad1f8e387d551ff&redirect_uri=https://example.com/oauth&response_type=code&scope=talk_message,friends")
        authorize_code = input()
        
        # access_token, 등을 받다오기 위한 주소
        url = 'https://kauth.kakao.com/oauth/token'
        rest_api_key = '11aa535784ec16106ad1f8e387d551ff'
        redirect_uri = 'https://example.com/oauth'
        
        # 요청 데이터 생성
        data = {
            'grant_type':'authorization_code',
            'client_id':rest_api_key,
            'redirect_uri':redirect_uri,
            'code': authorize_code,
        }

        # 요청을 보낸 후 결과를 변수에 저장
        response = requests.post(url, data=data)
        # json으로 변환 후 출력
        tokens = response.json()
        print("\n친구목록")
        print(tokens)

        # JSON 형태로 변환
        friend_list = self.getFriendList(tokens)
        print(friend_list,"\n")

        return tokens, friend_list

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

    def sendMessageToKakao(self, msg="에러코드", name="양시현"):
        token, friend_list = self.main() # 메세지를 전송할 준비
        
        found = False

        # 친구 목록에서 이름을 찾아 그 사람의 uuid를 전송
        for element in friend_list['elements']:
            if element['profile_nickname'] == name:
                code = self.sendMsg(msg, element['uuid'], token['access_token'])
                print(code)
                found = True
                if code == 200:
                    print("code 200: 정상 전송")
                elif code == 400:
                    print("code 400: 잘못된 요청")
                
                break

        if not found:
            # 해당 이름을 찾지 못한 경우 실행할 코드
            print("해당 이름을 찾을 수 없습니다.")


if __name__ == "__main__":
    a = AddFriend()
    a.sendMessageToKakao()
    