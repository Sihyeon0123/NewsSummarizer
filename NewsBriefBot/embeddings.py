# 자연어 검색을 위한 임베딩 모델입니다.
# 작성자: 양시현
# 수정 이력: 
# - 2024-04-26: 초기버전 생성

import numpy as np
from numpy.linalg import norm
import json
import requests

class Embedding:
    def __init__(self, apiKey) -> None:
        self.result = None
        self.apiKey = apiKey

    def temp(self, text="") -> list:
        model="text-embedding-3-small"
        response = self.client.embeddings.create(
            input = [text], 
            model=model
        ).data[0].embedding
        
        # print(response)
        jsonEmbedding = json.dumps(response)
        # print(jsonEmbedding)
        return jsonEmbedding
    
    def getEmbedding(self, text):
        url = "https://api.openai.com/v1/embeddings"
        requestData = {
            "input": text,
            "model": "text-embedding-3-small"
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.apiKey}"
        }

        # POST 요청 보내기
        response = requests.post(url, headers=headers, json=requestData)

        # 응답 상태 코드 확인
        statusCode = response.status_code

        # 응답 내용 확인
        responseBody = response.json()

        # embedding 추출
        embeddingNode = responseBody["data"][0]["embedding"]
        JsonString = json.dumps(embeddingNode)
        return JsonString
        
    # 코사인 거리 계산
    def cosineDist(this, a, b):
        return 1 - np.dot(a,b) / (norm(a)*norm(b))
