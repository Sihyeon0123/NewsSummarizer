# 네이버 실시간 뉴스를 저장할 클래스
# 작성자: 양시현
# 수정 이력: 
# - 2024-04-06: 초기버전 생성
from datetime import datetime

class NaverRealTimeNewsBody:
    def __init__ (self, url, title, imgURL, date:datetime, newspaper, category):
        # 뉴스 주소
        self.url = url
        # 뉴스 이미지 주소
        self.img_url = imgURL
        # 뉴스 제목
        self.title = title
        # 뉴스 작성일
        self.date = date
        # 뉴스 작성사
        self.newspaper = newspaper
        # 카테고리
        self.category = category

    # 객체 출력시 출력 형태
    def __str__(self):
        return f"주소: {self.url}, \n제목: {self.title}, \n날짜: {self.date} \n신문사: {self.newspaper} \n이미지 주소: {self.img_url} \n분야: {self.category}"
