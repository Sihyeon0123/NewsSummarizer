# 신문을 저장할 클래스를 정의합니다.
# 작성자: 양시현
# 수정 이력: 
# - 2024-02-04: 초기버전 생성
# - 2024-03-05: 수정날짜 분리
# - 2024-03-23: 콘텐츠 원본 추가, 카테고리 추가
# - 2024-03-24: 요약 뉴스 Setter 추가
# - 2024-04-30: 임베딩 속성 추가

class Article:
    def __init__ (self, url, title, img_url, date, update_date, original_news, newspaper, category):
        # 뉴스 주소
        self.url = url
        # 뉴스 이미지 주소
        self.img_url = img_url
        # 뉴스 제목
        self.title = title
        # 뉴스 작성일
        self.date = date
        # 뉴스 수정일
        self.update_date = update_date
        # 뉴스 원본
        self.original_news = original_news
        # 요약된 뉴스
        self.summarized_news = None
        # 뉴스 작성사
        self.newspaper = newspaper
        # 카테고리
        self.category = category
        # 임베딩
        self.embedding = None

    # 객체 출력시 출력 형태
    def __str__(self):
        return f"주소: {self.url}, \n제목: {self.title}, \n날짜: {self.date} \n수정날짜: {self.update_date}, \n신문사: {self.newspaper} \n이미지 주소: {self.img_url} \n분야: {self.category}"
    
    def setSummarizedNews(self, summarized_news):
        self.summarized_news = summarized_news

    def setEmbedding(self, embedding):
        self.embedding = embedding