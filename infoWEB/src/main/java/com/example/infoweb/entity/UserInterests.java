/*
 *   관심 분야 엔티티입니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.entity;

import jakarta.persistence.*;
import lombok.*;

@Getter
@Setter
@ToString
@AllArgsConstructor
@NoArgsConstructor
@Entity
public class UserInterests {

    @Id
    private String user_id;

    @Column(nullable = false)
    private Boolean politics = false;

    @Column(nullable = false)
    private Boolean economy = false;

    @Column(nullable = false)
    private Boolean society = false;

    @Column(nullable = false)
    private Boolean lifestyleCulture = false;

    @Column(nullable = false)
    private Boolean it = false;

    @Column(nullable = false)
    private Boolean world = false;

    @Column(nullable = false)
    private Boolean stock = false;

    @OneToOne
    @MapsId // UserInterests의 user_id 필드가 UserInfo의 id 필드와 동일한 값을 가지게 함
    @JoinColumn(name = "user_id")
    private UserInfo userInfo;

}
