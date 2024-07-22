/*
 *   Spring Data JPA의 CrudRepository 인터페이스를 상속받아
 *   기본적인 NaverNewsRepository 테이블의 CRUD 작업을 수행할 수 있는 메소드를 제공합니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.repository;

import com.example.infoweb.entity.NaverNews;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;

import java.util.ArrayList;

public interface NaverNewsRepository extends CrudRepository<NaverNews, String> {

    @Override
    // 오늘 날짜의 데이터가 없으면 가장 최근 날짜 조회
    @Query("SELECT n FROM NaverNews n WHERE DATE(n.created_at) = " +
            "(SELECT COALESCE((SELECT DATE(nn.created_at) FROM NaverNews nn WHERE DATE(nn.created_at) = CURRENT_DATE), " +
            "(SELECT MAX(DATE(nn.created_at)) FROM NaverNews nn)))")
    ArrayList<NaverNews> findAll();

    // category 문자열과 일치하는 오늘 날짜 NaverNews 엔티티 인스턴스를 내림차순으로 반환
    // 오늘 날짜의 데이터가 없으면 가장 최근 날짜 조회
    @Query("SELECT n FROM NaverNews n WHERE n.category = :category AND DATE(n.created_at) = " +
            "(SELECT COALESCE((SELECT DATE(nn.created_at) FROM NaverNews nn WHERE nn.category = :category AND DATE(nn.created_at) = CURRENT_DATE), " +
            "(SELECT MAX(DATE(nn.created_at)) FROM NaverNews nn WHERE nn.category = :category))) " +
            "ORDER BY n.id DESC")
    ArrayList<NaverNews> findByCategory(String category);

    /**
     * findBy: 이 메서드가 쿼리 메서드임을 나타내며, 결과를 찾기 위해 데이터베이스를 조회할 것을 나타냅니다.
     * Title: NaverNews 엔티티의 title 속성에 대한 조건을 나타냅니다.
     * Containing: LIKE '%keyword%'와 유사한 SQL 조건을 생성합니다. 즉, 주어진 문자열을 포함하는 title을 찾습니다.
     * IgnoreCase: 대소문자를 구분하지 않고 검색합니다.
     */
    ArrayList<NaverNews> findByTitleContainingIgnoreCase(String title);
}
