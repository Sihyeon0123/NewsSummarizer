/*
 *   Spring Data JPA의 CrudRepository 인터페이스를 상속받아
 *   기본적인 UserInterests 테이블의 CRUD 작업을 수행할 수 있는 메소드를 제공합니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.repository;

import com.example.infoweb.entity.UserInterests;
import org.springframework.data.repository.CrudRepository;

public interface UserInterestsRepository extends CrudRepository<UserInterests, String> {
    
}
