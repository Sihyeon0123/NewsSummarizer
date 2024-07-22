/*
 *   DB에서 회원정보를 받아온 후
 *   스프링부트에게 넘겨주는 클래스입니다.
 *   사용자 아이디로 사용자 정보를 조회하고
 *   스프링 시큐리티에서 사용할 수 있는 UserDetails 객체로 변환합니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.config;

import com.example.infoweb.entity.UserInfo;
import com.example.infoweb.service.UserService;
import lombok.AllArgsConstructor;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Component;
import java.util.Optional;

@AllArgsConstructor // 생성자
@Component
public class MyUserDetailService implements UserDetailsService {

    private final UserService userService;

    // Spring Security의 인증 과정에서 자동 호출
    @Override
    public UserDetails loadUserByUsername(String insertedUserId) throws UsernameNotFoundException {

        // 사용자 아이디로 DB에서 사용자 정보를 조회
        Optional<UserInfo> findOne = userService.findOne(insertedUserId);

        // 사용자 정보가 존재하지 않으면 예외처리
        UserInfo userInfo = findOne.orElseThrow(() -> new UsernameNotFoundException("등록되지 않은 회원입니다."));

        // 조회된 사용자 정보를 바탕으로 UserDetails 객체를 생성하여 반환
        return User.builder()
                   .username(userInfo.getId())
                   .password(userInfo.getPw())
                   .build();

    }

}
