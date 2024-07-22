/*
 *   Spring Data JPA의 CrudRepository 인터페이스를 상속받아
 *   기본적인 NaverRealTimeNews 테이블의 CRUD 작업을 수행할 수 있는 메소드를 제공합니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.repository;

import com.example.infoweb.entity.NaverRealTimeNews;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;

import java.util.ArrayList;

public interface RealTimeNewsRepository extends CrudRepository<NaverRealTimeNews, String> {

    @Override
    // 오늘 날짜의 데이터가 없으면 가장 최근 날짜 조회
    @Query("SELECT n FROM NaverRealTimeNews n WHERE DATE(n.created_at) = " +
            "(SELECT COALESCE((SELECT DATE(nn.created_at) FROM NaverRealTimeNews nn WHERE DATE(nn.created_at) = CURRENT_DATE), " +
            "(SELECT MAX(DATE(nn.created_at)) FROM NaverRealTimeNews nn)))")
    ArrayList<NaverRealTimeNews> findAll();

    // category 문자열과 일치하는 오늘 날짜 NaverRealTimeNews 엔티티 인스턴스를 내림차순으로 반환
    // 오늘 날짜의 데이터가 없으면 가장 최근 날짜 조회
    @Query("SELECT n FROM NaverRealTimeNews n WHERE n.category = :category AND DATE(n.created_at) = " +
            "(SELECT COALESCE((SELECT DATE(nn.created_at) FROM NaverRealTimeNews nn WHERE nn.category = :category AND DATE(nn.created_at) = CURRENT_DATE), " +
            "(SELECT MAX(DATE(nn.created_at)) FROM NaverRealTimeNews nn WHERE nn.category = :category))) " +
            "ORDER BY n.id DESC")
    ArrayList<NaverRealTimeNews> findByCategory(String category);

}
