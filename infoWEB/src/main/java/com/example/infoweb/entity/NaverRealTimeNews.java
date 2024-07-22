/*
 *   네이버 실시간 뉴스 엔티티입니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@ToString
@AllArgsConstructor
@NoArgsConstructor
@Entity
public class NaverRealTimeNews {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 255)
    private String title;

    @Column(nullable = false, length = 255, unique = true)
    private String news_url;

    @Column(length = 255)
    private String image_url;

    @Column(nullable = false, length = 50)
    private String publisher;

    @Column(nullable = false)
    private LocalDateTime created_at;

    @Column(nullable = false, length = 50)
    private String category;


}
