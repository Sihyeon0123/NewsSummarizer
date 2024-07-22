/*
 *   임베딩 벡터를 생성하고 코사인 유사도를 계산하는 클래스입니다.
 *
 *   작성자: 양시현
 *
 * */

package com.example.infoweb.embedding;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.math3.linear.MatrixUtils;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import java.io.IOException;
import java.nio.charset.StandardCharsets;


@Slf4j
public class Embedding {
    private double dot(double[] a, double[] b) {
        if (a.length != b.length) {
            return 0.0;
        }

        double dotProduct = 0;
        for (int i = 0; i < a.length; i++) {
            dotProduct += a[i] * b[i];
        }

        return dotProduct;
    }
    /**
     * maven
     * <dependency>
     *  <groupId>org.apache.commons</groupId>
     *  <artifactId>commons-math3</artifactId>
     *  <version>3.6.1</version>
     * </dependency>
     *
     *  gradle
     *  implementation 'org.apache.commons:commons-math3:3.6.1'
     *  코사인거리 계산
     * */
    public double cosineDistance(double[] vec1, double[] vec2) {
//        RealVector vectorA = MatrixUtils.createRealVector(vec1);
//        RealVector vectorB = MatrixUtils.createRealVector(vec2);
        double dotProduct = dot(vec1, vec2);
        double normVec1 = MatrixUtils.createRealVector(vec1).getNorm();
        double normVec2 = MatrixUtils.createRealVector(vec2).getNorm();

        return (dotProduct / (normVec1 * normVec2));
    }

    /**
     *      추가 필요
     *      maven
     *      <dependency>
     *      <groupId>org.apache.httpcomponents</groupId>
     *      <artifactId>httpclient</artifactId>
     *      <version>4.5.13</version>
     *      </dependency>
     *
     *      gradle
     *      implementation 'org.apache.httpcomponents:httpclient:4.5.13'
     *      검색어 임베딩 변환
     */
    public double[] getEmbedding(String text) {
        String url = "https://api.openai.com/v1/embeddings";
        String requestData = String.format("{\"input\": \"%s\", \"model\": \"text-embedding-3-small\"}", text);

        // HTTP 클라이언트 생성
        CloseableHttpClient httpClient = HttpClients.createDefault();
        try {
            // HTTP POST 요청 생성
            HttpPost httpPost = new HttpPost(url);

            // 요청 헤더 설정
            httpPost.setHeader("Content-Type", "application/json");
            httpPost.setHeader("Authorization", "Bearer sk-proj-Lae2ewjpQ3iY5KPYKutuT3BlbkFJJx42Vup9eDs8EG4ORiub");

            // 요청 바디 설정
            StringEntity entity = new StringEntity(requestData, StandardCharsets.UTF_8);
            httpPost.setEntity(entity);

            // 요청 전송 및 응답 수신
            HttpResponse response = httpClient.execute(httpPost);

            // 응답 상태 코드 확인
            int statusCode = response.getStatusLine().getStatusCode();

            if (statusCode != 200) {
                log.error("임베딩을 가져오지 못했습니다. 상태 코드: {}", statusCode);
                return new double[0];
            }

            // 응답 내용 출력
            HttpEntity responseEntity = response.getEntity();
            String responseBody = EntityUtils.toString(responseEntity);
//            System.out.println(responseBody);


            // JSON 파싱
            ObjectMapper mapper = new ObjectMapper();
            JsonNode jsonNode = mapper.readTree(responseBody);
            // "data" 배열의 첫 번째 요소 선택
            JsonNode dataNode = jsonNode.get("data");

            if (dataNode == null || !dataNode.isArray() || dataNode.size() == 0) {
                log.error("잘못된 응답 구조: 'data' 필드가 없거나 비어 있습니다.");
                return new double[0];
            }

            // embedding 필드의 값을 double 배열로 추출
            JsonNode embeddingNode = dataNode.get(0).get("embedding");

            if (embeddingNode == null || !embeddingNode.isArray()) {
                log.error("잘못된 응답 구조: 'embedding' 필드가 없거나 배열이 없습니다.");
                return new double[0];
            }

            return mapper.convertValue(embeddingNode, double[].class);

        } catch (IOException e) {
            log.error("임베딩을 가져오는 동안 예외 발생", e);
            return new double[0];
        }
    }
}
