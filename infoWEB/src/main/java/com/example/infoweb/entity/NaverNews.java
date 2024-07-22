/*
 *   네이버 뉴스 엔티티입니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.entity;

import com.example.infoweb.converter.EmbeddingConverter;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@ToString
@AllArgsConstructor
@NoArgsConstructor
@Entity
public class NaverNews {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 255)
    private String news_url;

    @Column(nullable = false, length = 100)
    private String title;

    @Lob
    @Column(nullable = false, columnDefinition = "LONGTEXT")
    private String summary;

    @Lob
    @Column(nullable = false, columnDefinition = "LONGTEXT")
    private String original;

    @Column(length = 255)
    private String image_url;

    @Column(nullable = false, length = 50)
    private String publisher;

    @Column(nullable = false)
    private LocalDateTime created_at;

    private LocalDateTime updated_at;

    @Column(nullable = false, length = 50)
    private String category;

    @Convert(converter = EmbeddingConverter.class)
    @Column(columnDefinition = "JSON", nullable = false)
    private double[] embedding;

    @Transient
    private double similarityScore;

}
