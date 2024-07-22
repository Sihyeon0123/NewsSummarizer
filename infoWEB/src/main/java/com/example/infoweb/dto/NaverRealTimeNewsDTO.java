/*
 *   실시간 뉴스 데이터를 전달받아 날짜를 포맷팅하는 DTO 입니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.dto;

import com.example.infoweb.entity.NaverRealTimeNews;
import lombok.Getter;
import lombok.Setter;

import java.time.format.DateTimeFormatter;

@Getter
@Setter
public class NaverRealTimeNewsDTO {

    private Long id;
    private String title;
    private String news_url;
    private String image_url;
    private String publisher;
    private String created_at;
    private String category;

    public NaverRealTimeNewsDTO(NaverRealTimeNews news, DateTimeFormatter formatter) {
        this.id = news.getId();
        this.title = news.getTitle();
        this.news_url = news.getNews_url();
        this.image_url = news.getImage_url();
        this.publisher = news.getPublisher();
        this.created_at = news.getCreated_at().format(formatter);   // 날짜 포맷팅
        this.category = news.getCategory();
    }

}
