/*
 *   메인 페이지 컨트롤러입니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.controller;

import com.example.infoweb.dto.NaverNewsDTO;
import com.example.infoweb.dto.NaverRealTimeNewsDTO;
import com.example.infoweb.entity.*;
import com.example.infoweb.repository.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.User;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

@Slf4j
@Controller
public class MainController {

    @Autowired  // 의존성 주입
    private NaverNewsRepository naverNewsRepository;
    @Autowired
    private UserRepository userRepository;
    @Autowired
    private UserInterestsRepository userInterestsRepository;
    @Autowired
    private RealTimeNewsRepository realTimeNewsRepository;
    @Autowired
    private NounFrequencyRepository nounFrequencyRepository;
    @Autowired
    private FinvizMapRepository finvizMapRepository;
    @Autowired
    private FinancialjuiceRepository financialjuiceRepository;
    @Autowired
    private InvestingRealTimeRepository investingRealTimeRepository;

    // 이미 로드된 뉴스 URL을 저장하는 Set
    private Set<String> loadedNewsUrls = new HashSet<>();
    // 카테고리에 따라 필터링 된 메인 뉴스를 전역 변수로
    Iterable<NaverNews> filteredNews;
    // 날짜 포맷터
    DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd a hh:mm");

    /**
     * 메인 페이지 폼
     * */
    @GetMapping("/main")
    public String newMainForm(@AuthenticationPrincipal User user, @RequestParam(defaultValue = "종합") String category, Model model) {
        /*
         *   @AuthenticationPrincipal: 현재 인증된 사용자의 정보를 메서드의 파라미터로 직접 주입할 때 사용
         *   @RequestParam: HTTP 요청의 파라미터를 컨트롤러 메서드의 파라미터에 바인딩할 때 사용
         *
         * */

        // 중복 저장 초기화
        loadedNewsUrls = new HashSet<>();

        // 로그인하지 않았을 때
        UserInterests userInterests = null;

        // 로그인되어 있는 유저 정보를 가져옴
        if (user != null) {
            model.addAttribute("loginInfo", user.getUsername());
            log.info("현재 로그인 정보 " + user.getUsername());

            // 로그인된 사용자의 관심분야를 가져옴
            userInterests = userInterestsRepository.findById(Objects.requireNonNull(user).getUsername()).orElse(null);
        }

        model.addAttribute("userInterests", userInterests);
        log.info("사용자 관심분야 가져오기 완료");

        // 카테고리가 종합일 경우 랜덤 뉴스 조회
        if (category.equals("종합")) {
            // 랜덤으로 메인 뉴스 가져오기
            filteredNews = naverNewsRepository.findAll()
                                              .stream()
                                              .collect(Collectors.collectingAndThen(Collectors.toList(), collected -> {
                                                  Collections.shuffle(collected);
                                                  return collected.stream();
                                              }))
                                              .limit(8)
                                              .collect(Collectors.toList());
            log.info("랜덤 메인 뉴스 가져오기 완료");

        } else {
            // 카테고리에 따라 필터링된 메인 뉴스 가져오기
            filteredNews = naverNewsRepository.findByCategory(category)
                                              .stream()
                                              .limit(8)
                                              .collect(Collectors.toList());
            log.info("카테고리 별 메인 뉴스 가져오기 완료");

        }

        model.addAttribute("naverNewsList", filteredNews);
        log.info(category + "로 필터링된 메인 뉴스 데이터 조회");

        // 카테고리 선택했을 때 불 들어오게
        model.addAttribute("selectedCategory", category);

        // 키워드 가져오기
        Iterable<NounFrequency> nounFrequencies = StreamSupport.stream(nounFrequencyRepository.findAll().spliterator(), false)
                .limit(16)
                .collect(Collectors.toList());

        model.addAttribute("nounFrequencies", nounFrequencies);

        return "/main";
    }

    /**
     * 마이페이지 폼
     * */
    @GetMapping("/users/mypage")
    public String myPageForm(@AuthenticationPrincipal User user, Model model) {

        // 로그인되어 있는 유저 정보를 가져옴
        if (user != null) {

            // UserInfo DB 조회
            UserInfo userInfo = userRepository.findByid(user.getUsername()).orElse(null);

            model.addAttribute("loginInfo", user.getUsername());
            log.info("마이페이지 로그인 정보" + user.getUsername());

            model.addAttribute("nameInfo", Objects.requireNonNull(userInfo).getName());
            log.info("마이페이지 이름 정보" + userInfo.getName());

            // 관심분야가 true면 체크박스 체크
            // th:checked="${userInterests.필드명}"은 UserInterests 객체의 해당 필드 값이 true인 경우 체크박스가 자동으로 선택되도록 한다
            UserInterests userInterests = userInterestsRepository.findById(user.getUsername()).orElse(new UserInterests());
            model.addAttribute("userInterests", userInterests);

        } else {
            return "/users/login";
        }

        return "/users/mypage";
    }

    /**
     * 실시간 뉴스를 추가로 로드하는 API
     */
    @GetMapping("/real_time_news")
    @ResponseBody
    public List<NaverRealTimeNewsDTO> loadMoreRealTimeNews(@RequestParam String category, @RequestParam int offset, @RequestParam int limit) {

        if (category.equals("종합")) {
            // 모든 실시간 뉴스를 가져옴
            List<NaverRealTimeNews> allNews = realTimeNewsRepository.findAll();

            // 이미 로드된 뉴스 URL을 제외하고 랜덤으로 뉴스를 선택
            List<NaverRealTimeNews> randomNews = allNews.stream()
                                                .filter(news -> !loadedNewsUrls.contains(news.getNews_url()))
                                                // 이미 로드된 뉴스 제외
                                                .collect(Collectors.collectingAndThen(Collectors.toList(), collected -> {
                                                    // 리스트를 셔플하여 무작위 순서로 정렬
                                                    Collections.shuffle(collected);
                                                    return collected.stream();
                                                }))
                                                // 지정된 수만큼 뉴스를 선택
                                                .limit(limit)
                                                .collect(Collectors.toList());
            // 로드된 뉴스 URL을 Set에 추가하여 중복 로드를 방지
            loadedNewsUrls.addAll(randomNews.stream().map(NaverRealTimeNews::getNews_url).toList());
            log.info("종합 랜덤 실시간 뉴스 가져오기 완료");
            // 선택된 뉴스를 포맷팅하여 리턴
            return randomNews.stream()
                    .map(news -> new NaverRealTimeNewsDTO(news, formatter))
                    .collect(Collectors.toList());
        } else {
            log.info("카테고리 별 실시간 뉴스 가져오기 완료");
            // 해당 카테고리의 뉴스를 페이징하여 가져옴
            return realTimeNewsRepository.findByCategory(category)
                                         .stream()
                                         .skip(offset)  // 오프셋부터 시작
                                         .limit(limit)  // 지정된 수만큼 뉴스를 가져옴
                                         .map(news -> new NaverRealTimeNewsDTO(news, formatter))  // 날짜 포맷팅
                                         .collect(Collectors.toList());
        }
    }

    /**
     * 뉴스 조회 폼
     * */
    @GetMapping("/article")
    public String articleForm(@RequestParam Long id, Model model) {

        // 뉴스 ID로 뉴스 정보를 가져옴
        Optional<NaverNews> newsInfo = naverNewsRepository.findById(String.valueOf(id));

        // 뉴스가 존재하지 않으면 404 페이지로 이동
        if (newsInfo.isEmpty()) {
            log.info("article - 해당 뉴스가 존재하지 않습니다.");
            return "404";
        }

        NaverNews articleNews = newsInfo.get();
        model.addAttribute("articleNews", articleNews);
        log.info("article - 해당 뉴스 요약 불러오기 완료");

        // 날짜 포맷
        String formattedDate = articleNews.getCreated_at().format(formatter);
        model.addAttribute("formattedDate", formattedDate);
        log.info("article - 날짜 포맷 완료");

        // article 페이지에 접속할 때, 전역 변수인 filteredNews를 사용하여 조회할 뉴스를 제외한 나머지 메인 뉴스들을 최근 뉴스 리스트로 가져옴
        model.addAttribute("recentNewsList", ((List<NaverNews>) filteredNews).stream()
                                                                                         // 날짜 포맷팅
                                                                                         .map(news -> new NaverNewsDTO(news, formatter))
                                                                                         // 현재 뉴스 제외
                                                                                         .filter(n -> !n.getId().equals(articleNews.getId()))
                                                                                         .collect(Collectors.toList()));
        log.info("article - 최근 뉴스 리스트 불러오기 완료");

        return "/article";

    }

    /**
     * 주식 카테고리 폼
     * */
    @GetMapping("/investing")
    public String investingForm(Model model) {

        // FinvizMap url 레코드 가져옴
        FinvizMap finvizMapUrl = finvizMapRepository.findLatestEntry();
        model.addAttribute("finvizMapUrl", finvizMapUrl);
        log.info("주식 - url 레코드 가져옴");

        // InvestingRealTime 엔티티 가져옴
        Iterable<InvestingRealTimeEvents> investingRealTimeEvents = investingRealTimeRepository.findAllDescLimit();
        model.addAttribute("investingRealTime", investingRealTimeEvents);
        log.info("주식 - InvestingRealTime 엔티티 가져옴");

        // FinancialjuiceEvents 엔티티 가져옴
        Iterable<FinancialjuiceEvents> financialjuiceEvents = financialjuiceRepository.findAllDescLimit();
        model.addAttribute("financialjuice", financialjuiceEvents);
        log.info("주식 - FinancialjuiceEvents 엔티티 가져옴");

        return "/investing";
    }

}
