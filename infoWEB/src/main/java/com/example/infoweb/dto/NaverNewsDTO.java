/*
 *   뉴스 데이터를 전달받아 날짜를 포맷팅하는 DTO 입니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.dto;

import com.example.infoweb.entity.NaverNews;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Getter
@Setter
public class NaverNewsDTO {

    private Long id;
    private String news_url;
    private String title;
    private String summary;
    private String original;
    private String image_url;
    private String publisher;
    private String created_at;
    private LocalDateTime updated_at;
    private String category;
    private double[] embedding;
    private double similarityScore;

    public NaverNewsDTO(NaverNews news, DateTimeFormatter formatter) {
        this.id = news.getId();
        this.news_url = news.getNews_url();
        this.title = news.getTitle();
        this.publisher = news.getPublisher();
        this.summary = news.getSummary();
        this.original = news.getOriginal();
        this.image_url = news.getImage_url();
        this.created_at = news.getCreated_at().format(formatter);   // 날짜 포맷팅
        this.updated_at = news.getUpdated_at();
        this.embedding = news.getEmbedding();
        this.category = news.getCategory();
        this.similarityScore = news.getSimilarityScore();
    }
}
