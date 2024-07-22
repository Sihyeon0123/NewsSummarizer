# investing 캘린더의 정보를 저장할 클래스
# 작성자: 양시현
# 수정 이력: 
# - 2024-04-06: 초기버전 생성

class InvestingInfoBody:
    def __init__ (self, url, date, country, importance, eventDescription, forecast, actual, previous):
        # 주소
        self.url = url
        # 이벤트 일자
        self.date = date
        # 나라
        self.country = country
        # 중요도
        self.importance = importance
        # 이벤트
        self.eventDescription = eventDescription
        # 예측
        self.forecast = forecast
        # 실제
        self.actual = actual
        # 이전  
        self.previous = previous
