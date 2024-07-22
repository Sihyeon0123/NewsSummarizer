/*
 *   회원가입 폼 데이터를 전달받는 DTO 입니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.dto;

import com.example.infoweb.entity.UserInfo;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@Getter
@Setter
@ToString           // 데이터를 잘 받았는지 확인할 toString() 자동화
@AllArgsConstructor // 전송받은 제목과 내용을 필드에 저장하는 생성자 자동화
public class UserForm {

    private String id;
    private String pw;
    private String mpw; // 수정할 비밀번호
    private String cpw; // 수정할 비밀번호 확인
    private String name;

    private String politics;
    private String economy;
    private String society;
    private String lifestyleCulture;
    private String it;
    private String world;
    private String stock;

    private final PasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public UserInfo toEntity() {
        return new UserInfo(id, passwordEncoder.encode(pw), name);
    }

}
