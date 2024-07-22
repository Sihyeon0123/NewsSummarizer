# GPT API를 통해 뉴스나 정보를 요약합니다!
# 작성자: 양시현
# 수정 이력: 
# - 2024-02-04: 초기버전 생성
# - 2024-03-23: 클래스로 리팩토링
# - 2024-04-30: embeddings 추가, apiKey 변수 추가
# - 2024-05-26: 가독성을 위해 ".", ". "을 줄바꿈(.\n)으로 변경

import queue
import threading
import time
import logging
import os
from openai import OpenAI # pip install openai
import re

from article import Article
import naverNewsDAO
import embeddings 

class NewsBriefBot:
	def __init__(self) -> None:
		self.apiKey = ""
		self.client = OpenAI(api_key=self.apiKey)
		self.logger = None
		self.dao = naverNewsDAO.NaverNewsDAO()

	def setupLogger(self, name, log_file, level=logging.DEBUG):
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
		handler = logging.FileHandler(log_file, encoding='utf-8')
		handler.setFormatter(formatter)

		self.logger = logging.getLogger(name)
		self.logger.setLevel(level)
		self.logger.addHandler(handler)


	def createAssistant(self) -> dict:
		# 어시던트 생성
		news_assistant = self.client.beta.assistants.create(
			name="NewsBriefBot",
			instructions="Please summarize this content in 100tokens or less. Please answer in Korean",
			model="gpt-3.5-turbo-1106",
		)

		# 쓰레드 생성
		news_thread = self.client.beta.threads.create()
		
		return {'assistant_id': news_assistant.id, 'thread_id': news_thread.id}


	def brief(self, ids, msg):
		# 쓰레드에 메시지 추가
		thread_message = self.client.beta.threads.messages.create(
			thread_id = ids['thread_id'],
			role="user",
			content=msg,
		)
		# print(thread_message, end="\n\n")

		# 메시지를 실행
		run = self.client.beta.threads.runs.create(
			thread_id=ids['thread_id'],
			assistant_id=ids['assistant_id'],
		)
		# 실행한 메시지의 결과가 생성되었는지 반복적으로 확인하며 대기
		while True:
			time.sleep(3)
			run = self.client.beta.threads.runs.retrieve(
				thread_id=ids['thread_id'],
				run_id=run.id
			)
			if run.status == "completed":
				# print(run)
				self.logger.debug('정상적으로 요약값을 받았습니다.')
				break
			elif run.status == "failed":    
				self.logger.debug('요청횟수를 모두 사용하여 대기합니다.')
				time.sleep(60)
				run = self.client.beta.threads.runs.create(
					thread_id=ids['thread_id'],
					assistant_id=ids['assistant_id'],
				)
			else :
				self.logger.debug('처리 중..')

		thread_message = self.client.beta.threads.messages.list(ids['thread_id'],)
		return thread_message.data[0].content[0].text.value


	def formattingNews(self, news:Article) -> str:
		"""
		GPT에게 전달할 뉴스 형식을 생성합니다.
		"""
		formatted_text = f"제목: {news.title}\n본문: {news.original_news}"
		return formatted_text


	def runBrief(self, global_task_queue: queue.Queue, queue_event: threading.Event):
		log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
		self.setupLogger("newsBriefBot", os.path.join(log_dir, "newsBriefBot.log")) # logger 설정
		self.logger = logging.getLogger("newsBriefBot")
		self.logger.info('브리핑 봇 시작')

		# 임베딩 모델 생성
		embeddingModel = embeddings.Embedding(self.apiKey)
		while True:
			# 메시지 실행
			queue_event.wait() # 이벤트 대기

			if not global_task_queue.empty():
				news: Article = global_task_queue.get()
				news_thread = self.client.beta.threads.create()
				ids = {'assistant_id': 'asst_3twHpxsoqsCeqUzu4QwJ6SYK', 'thread_id': f'{news_thread.id}'}
				# print(ids)
				self.logger.info('큐에서 작업 획득 완료 요청 수행')
				# 뉴스 요약
				SummarizedNews = self.brief(ids, self.formattingNews(news))    
				
				# "."과 ". "을 구별하지 못하여 제거
				# SummarizedNews = SummarizedNews.replace(".", ".\n")
				SummarizedNews = re.sub(r'\.\s*', '.\n', SummarizedNews)
				news.setSummarizedNews(SummarizedNews)
				# 임베딩 생성
				news.setEmbedding(embeddingModel.getEmbedding(news.title))
				self.dao.connect()
				self.dao.insert_news(news)
				self.dao.disconnect()
				self.logger.info('요약 완료')
				self.logger.debug("제목:"+news.title+"\n"+SummarizedNews)
			else:
				self.logger.info('대기중인 작업이 없어 대기로 전환')
				queue_event.clear() # 대기상태로 전환
				time.sleep(5)