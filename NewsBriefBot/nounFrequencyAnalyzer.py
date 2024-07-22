# 신문에 나오는 명사 빈도수 계산 및 시각화 클래스
# 작성자: 양시현
# 수정 이력: 
# - 2024-03-23: 초기버전 생성
# - 2024-04-17: 배경 투명하게 변경, 이미지 크기 변경, 워드클라우드 모양 추가

from collections import Counter
from konlpy.tag import Okt
from wordcloud import WordCloud
import matplotlib
import matplotlib.pyplot as plt
import naverNewsDAO
import logging
import os
from datetime import datetime
import numpy as np
from PIL import Image
from datetime import datetime

IMG_W = 1920
IMG_H = 1080

class NounFrequencyAnalyzer:
    def __init__(self) -> None:
        self.dao = naverNewsDAO.NaverNewsDAO()
        self.okt = Okt()
        self.nouns_list = []
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.setup_logger("nounFrequencyAnalyzer", os.path.join(log_dir, "nounFrequencyAnalyzer.log")) # logger 설정
        self.logger = logging.getLogger("system")
        self.stopwords = set(['것', '명', '감', '중', '몇', '곳', '데', '등', '기',
                              '및', '조', '고', '이', '전', '수', '며', '위', '윤', '말', '룰', '를', '관련', '도'])  # 불용어 목록

    def setup_logger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)

    def extract_nouns(self):
        self.dao.connect()
        news_data = self.dao.select_news()
        self.dao.disconnect()

        if news_data is None:
            self.logger.info("DB에 저장된 항목이 존재하지 않아 대기상태로 전환합니다.")
            import time
            time.sleep(300) 

        for news in news_data:
            temp = news['original']
            nouns = self.okt.nouns(temp)
            filtered_nouns = [noun for noun in nouns if noun not in self.stopwords]  # 불용어 제거
            self.nouns_list.extend(filtered_nouns)
    
    def calculate_noun_frequency(self):
        noun_freq = {}
        for noun in self.nouns_list:
            if noun in noun_freq:
                noun_freq[noun] += 1
            else:
                noun_freq[noun] = 1
        sorted_noun_freq = sorted(noun_freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_noun_freq
       
    def save_frequencies(self, frequencies, count):
        # 현재 날짜와 시간을 가져오기
        today = datetime.now()
        # 날짜만 추출
        date_today = today.date()
    
        self.dao.connect()
        self.dao.insert_frequency(date_today, frequencies, count)
        self.dao.disconnect()

    def createImage(self):
        self.logger.info("이미지 생성 및 빈도 분석을 시작합니다.")
        images_dir = os.path.join(os.path.dirname(__file__), '..', 'infoWEB', 'src', 'main', 'resources', 'static', 'images')
        # images_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
        mask_path = os.path.join(images_dir, 'mask.png')  # 마스크 이미지 경로
        font_file_path = os.path.join(os.path.dirname(__file__), 'font', 'malgun.ttf')
        current_time = datetime.now().strftime("%Y-%m-%d")
        image_filename = f"wordcloud_{current_time}.png"
        self.extract_nouns()
        noun_frequencies = self.calculate_noun_frequency()
        self.save_frequencies(noun_frequencies, 10) # 10개 만큼 (단어, 빈도) 저장
        self.logger.info("빈도 분석 완료")
        
        # 마스크 이미지 로드 및 변환
        mask_image = np.array(Image.open(mask_path).resize((IMG_W, IMG_H)))

        wordcloud = WordCloud(font_path=font_file_path,
                              background_color=None,
                              mode='RGBA',
                              width=IMG_W, height=IMG_H,
                              max_words=400,
                              mask=mask_image).generate_from_frequencies(dict(noun_frequencies))
        
        # 그림 그리기
        matplotlib.use('Agg')
        plt.figure(figsize=(25, 14))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')

        # 그림 저장
        plt.savefig(os.path.join(images_dir, image_filename), bbox_inches='tight', format='png')
        # plt.savefig(os.path.join(images_dir, image_filename), bbox_inches='tight', format='png', transparent=True)
        self.logger.info("이미지 생성 완료")

