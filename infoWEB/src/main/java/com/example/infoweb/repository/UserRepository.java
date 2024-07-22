/*
 *   변환한 UserInfo 엔티티를 DB에 저장하는 리포지토리 클래스입니다.
 *   Spring Data JPA의 CrudRepository 인터페이스를 상속받아 기본적인 CRUD 작업을 수행할 수 있는 메소드를 제공합니다.
 *
 *   또한 사용자 아이디를 기반으로 사용자 정보를 조회하는 기능을 추가로 제공합니다.
 *   findByid 메소드를 통해 특정 ID를 가진 UserInfo 엔티티를 조회할 수 있습니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.repository;

import com.example.infoweb.entity.UserInfo;
import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

public interface UserRepository extends CrudRepository<UserInfo, String> {

    // 사용자 아이디로 UserInfo 엔티티를 조회하는 메소드
    // 조회 결과가 없을 수 있으므로, Optional로 감싸서 반환
    Optional<UserInfo> findByid(String id);
    Optional<UserInfo> findByPw(String Pw);
}
