/*
 *   FinancialjuiceEvents 테이블의 엔티티입니다.
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
public class FinancialjuiceEvents {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(length = 255)
    private String url;

    private LocalDateTime event_time;

    @Column(length = 255)
    private String event_description;

}