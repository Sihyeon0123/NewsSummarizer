/*
 *   InvestingRealTimeEvents 테이블 엔티티입니다.
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
public class InvestingRealTimeEvents {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 255)
    private String url;

    @Column
    private LocalDateTime event_time;

    @Column(length = 100)
    private String country;

    @Column
    private Integer importance;

    @Column(length = 255)
    private String event_description;

    @Column(length = 50)
    private String actual;

    @Column(length = 50)
    private String forecast;

    @Column(length = 50)
    private String previous;

}
