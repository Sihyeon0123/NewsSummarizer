/*
 *   UserInfo 엔티티에 대한 데이터 접근을 관리하는 서비스 클래스입니다.
 *   UserRepository 인터페이스를 사용하여 DB와의 상호작용을 수행하며,
 *   특정 사용자의 정보를 조회하는 기능을 제공합니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.service;

import com.example.infoweb.entity.UserInfo;
import com.example.infoweb.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserService {

    private final UserRepository repository;

    @Autowired  // 의존성 주입
    public UserService(UserRepository repository) {
        this.repository = repository;
    }

    // 사용자 아이디로 사용자 정보를 조회하는 메소드
    public Optional<UserInfo> findOne(String id) {
        return repository.findByid(id);
    }

}
