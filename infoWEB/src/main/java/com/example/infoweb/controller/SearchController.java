/*
 *   검색 페이지 컨트롤러입니다.
 *
 *   먼저 Like 연산을 이용해 데이터를 검색한 뒤 후순위로 유사도 측정 방식을 이용합니다.
 *   코사인 유사도를 이용한 유사도 측정 방식에서는 유사도 점수가 1에 가까울수록 더 유사하고, 0에 가까울수록 유사하지 않음을 나타냅니다.
 *
 *   유사도 점수:
 *    1: 두 벡터가 동일한 방향을 가리키며 가장 유사한 경우
 *    0: 두 벡터가 서로 직각을 이뤄 전혀 관련이 없는 경우
 *   -1: 두 벡터가 정반대 방향을 가리키며 완전히 상반되는 경우
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.controller;

import com.example.infoweb.dto.NaverNewsDTO;
import com.example.infoweb.embedding.Embedding;
import com.example.infoweb.entity.NaverNews;
import com.example.infoweb.repository.NaverNewsRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Controller
public class SearchController {

    @Autowired  // 의존성 주입
    private NaverNewsRepository naverNewsRepository;
    // 날짜 포맷터
    DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd a hh:mm");

    /**
     * 검색 페이지 폼을 처리하는 메서드
     *
     * @param searchKeyword 검색 키워드
     * @param model         뷰에 데이터를 전달하기 위한 모델
     * @return 검색 결과 페이지 뷰 이름
     */
    @GetMapping("/search")
    public String searchForm(
            @RequestParam(name = "searchKeyword", required = false) String searchKeyword,
            @RequestParam(name = "page", defaultValue = "0") int page, // 기본값 0, 페이지 번호를 받음
            Model model) {

        // 검색 키워드가 null이 아니고 공백이 아닐 때만 검색 수행
        if (searchKeyword != null && !searchKeyword.trim().isEmpty()) {
            log.info("검색 키워드: " + searchKeyword);

            // 검색 결과를 가져와서 finalResults 리스트에 저장
            List<NaverNewsDTO> finalResults = getSearchResults(searchKeyword, page); // 페이지 번호에 맞는 결과 요청
            // 모델에 검색 결과 리스트 추가
            model.addAttribute("results", finalResults);
            // 모델에 검색 키워드 추가
            model.addAttribute("searchKeyword", searchKeyword);
            // 모델에 페이지 번호 추가
            model.addAttribute("page", page);

            log.info("검색 결과 불러오기 완료");
        }

        return "/search";
    }

    /**
     * POST 방식으로 검색어를 받아 리다이렉트로 GET 요청을 수행하는 메서드
     * 검색어를 RedirectAttributes를 통해 전달하여 양식 제출 확인 메시지를 방지
     */
    @PostMapping("/search")
    public String searchPost(@RequestParam("searchKeyword") String searchKeyword, RedirectAttributes redirectAttributes) {

        log.info("검색 키워드 (POST): " + searchKeyword);

        // 검색 내용을 리다이렉트 파라미터로 추가
        redirectAttributes.addAttribute("searchKeyword", searchKeyword);

        // GET 요청으로 리다이렉트
        return "redirect:/search";

    }

    /**
     * 검색 결과를 페이지 단위로 반환하는 API
     * @param searchKeyword 검색 키워드
     * @param page 페이지 번호
     * @return 검색 결과 리스트
     */
    @GetMapping("/api/search")
    @ResponseBody
    public List<NaverNewsDTO> getSearchResults(@RequestParam("searchKeyword") String searchKeyword, @RequestParam("page") int page) {

        int pageSize = 100; // 한 번에 100개씩 가져오기

        // 코사인 유사도 검색 수행
        Embedding em = new Embedding();
        // 임베딩 계산
        double[] searchEmbedding = em.getEmbedding(searchKeyword);

        // Like 연산으로 검색 수행
        List<NaverNews> keywordResults = naverNewsRepository
                .findByTitleContainingIgnoreCase(searchKeyword)
                .stream()
                .toList();

        // 페이징 처리: 최신 뉴스 100개씩 페이지 범위에 맞는 데이터를 조회
        Pageable pageable = PageRequest.of(page, pageSize, Sort.by(Sort.Order.desc("createdAt")));
        Page<NaverNews> pageResults = naverNewsRepository.findAll(pageable);  // 페이지에 맞게 데이터 조회

        // 코사인 유사도 계산
        List<NaverNews> cosineResults = new ArrayList<>();
        for (NaverNews news : pageResults.getContent()) {
            double similarity = em.cosineDistance(searchEmbedding, news.getEmbedding());
            news.getClass(similarity);
            cosineResults.add(news);
        }

        // 유사도 점수가 높은 순서대로 정렬
        List<NaverNews> topResults = cosineResults.stream()
                .sorted(Comparator.comparingDouble(NaverNews::getSimilarityScore).reversed())
                .toList();

        // Like 연산 결과와 유사도 검색 결과 합치기
        List<NaverNews> combinedResults = new ArrayList<>(keywordResults);
        combinedResults.addAll(topResults);

        // 중복 제거 및 최종 결과 정렬
        List<NaverNews> finalResults = combinedResults.stream()
                .distinct()
                .sorted(Comparator.comparingDouble(NaverNews::getSimilarityScore).reversed())
                .collect(Collectors.toList());

        log.info("getSearchResults 함수 수행 완료");

        // finalResults을 리턴
        return finalResults.stream()
                // 날짜 포맷팅
                .map(news -> new NaverNewsDTO(news, formatter))
                .collect(Collectors.toList());
    }

}
