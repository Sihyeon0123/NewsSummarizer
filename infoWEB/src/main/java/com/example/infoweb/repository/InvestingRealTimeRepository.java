/*
 *   Spring Data JPA의 CrudRepository 인터페이스를 상속받아
 *   기본적인 InvestingRealTimeEvents 테이블의 CRUD 작업을 수행할 수 있는 메소드를 제공합니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.repository;

import com.example.infoweb.entity.InvestingRealTimeEvents;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;

public interface InvestingRealTimeRepository extends CrudRepository<InvestingRealTimeEvents, String> {

    // event_time 필드를 기준으로 가장 빠른 날짜의 값을 가져오는 쿼리
    @Query(value = "SELECT * FROM InvestingRealTimeEvents WHERE country = '미국' ORDER BY event_time LIMIT 12", nativeQuery = true)
    Iterable<InvestingRealTimeEvents> findAllDescLimit();

}
