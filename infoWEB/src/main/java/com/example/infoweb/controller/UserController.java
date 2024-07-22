/*
 *   유저 데이터 관리를 위한 컨트롤러입니다.
 *
 *   작성자: 이준영
 *
 * */

package com.example.infoweb.controller;

import com.example.infoweb.dto.UserForm;
import com.example.infoweb.entity.UserInfo;
import com.example.infoweb.entity.UserInterests;
import com.example.infoweb.repository.UserInterestsRepository;
import com.example.infoweb.repository.UserRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

import java.util.Objects;
import java.util.Optional;

@Slf4j  // 로깅 기능을 위한 어노테이션
@Controller
public class UserController {

    @Autowired  // 의존성 주입
    private UserRepository userRepository;
    @Autowired
    private UserInterestsRepository userInterestsRepository;
    private final PasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    /**
     * 회원가입 페이지 접속
     * */
    @GetMapping("/users/signup")
    public String newUserForm() {
        return "/users/SignUp";
    }

    /**
     * 로그인 페이지 접속
     * */
    @GetMapping("/users/login")
    public String loginUserForm(@AuthenticationPrincipal User user) {

        if (user != null) {
            return "/main";
        }

        return "/users/SignIn";
    }

    /**
     * 로그인 에러 처리
     * */
    @PostMapping("/loginError")
    public String loginError(UserForm form, Model model) {

        // 로그인 정보 확인
        UserInfo userInfo = form.toEntity();
        Optional<UserInfo> loginError = userRepository.findByid(userInfo.getId());
        if (loginError.isEmpty()) {
            model.addAttribute("loginError", "존재하지 않는 회원입니다.");
            log.info("로그인 - 존재하지 않는 회원 에러");
            return "/users/SignIn";
        }

        // 비밀번호 확인
        loginError = userRepository.findByPw(userInfo.getId());
        if (loginError.isEmpty()) {
            model.addAttribute("pwError", "비밀번호가 일치하지 않습니다.");
            log.info("로그인 - 비밀번호 에러");
            return "/users/SignIn";
        }

        return "/users/SignIn";

    }

    /**
     * 회원가입 처리
     * */
    @PostMapping("/users/create")
    public String createUser(UserForm form, Model model) {

        log.info("회원정보 생성 요청");

        // pw와 cpw 비교 (비밀번호 확인)
        if (!Objects.equals(form.getCpw(), form.getPw())) {
            model.addAttribute("passwordError", "비밀번호가 일치하지 않습니다.");
            log.info("회원가입 - 비밀번호 confirm 에러");
            return "/users/SignUp";
        }

        // DTO를 엔티티로 변환
        UserInfo userEntity = form.toEntity();
        log.info("UserInfo 엔티티 변환 완료");

        // 중복 회원 검증
        // isPresent(): Optional 객체가 값을 가지고 있다면 true, 값이 없다면 false 리턴
        Optional<UserInfo> validate = userRepository.findByid(userEntity.getId());
        if (validate.isPresent()) {
            model.addAttribute("overlapError", "이미 존재하는 ID 입니다.");
            log.info("중복 회원 에러");
            return "/users/SignUp";
        }

        // 리포지토리로 엔티티를 DB에 저장
        UserInfo saved = userRepository.save(userEntity);
        log.info("UserInfo DB 저장 완료");

        // UserInterests 테이블에도 id 저장
        UserInterests userInterests = new UserInterests();
        // 연관 관계 설정 (UserInterests의 user_id 필드가 UserInfo의 id 필드와 동일한 값을 가지게 함)
        userInterests.setUserInfo(saved);

        userInterests.setPolitics(true);                // 회원가입시 모든 분야 true
        userInterests.setEconomy(true);
        userInterests.setSociety(true);
        userInterests.setLifestyleCulture(true);
        userInterests.setIt(true);
        userInterests.setWorld(true);
        userInterests.setStock(true);

        userInterestsRepository.save(userInterests);    // DB에 저장
        log.info("회원가입시 관심분야 DB 저장 완료");

        // 성공적으로 회원가입이 끝나면 로그인 페이지로 리다이렉트
        return "redirect:/users/login";
    }

    /**
     * 회원정보 업데이트 처리
     * */
    @PostMapping("/users/update")
    public String updateUser(@AuthenticationPrincipal User user, UserForm form, Model model) {

        log.info("비밀번호 수정 요청");

        // 로그인 정보 가져오기
        UserInfo userEntity = userRepository.findByid(user.getUsername()).orElse(null);
        UserInterests userInterests = userInterestsRepository.findById(user.getUsername()).orElse(new UserInterests());

        if (userEntity == null) {
            log.info("로그인 정보가 유효하지 않습니다.");
            return "redirect:/users/login";
        }

        // 비밀번호 확인
        boolean passwordError = false;
        if (form.getPw() != null && !form.getPw().isEmpty() && form.getMpw() != null && form.getCpw() != null) {
            if (passwordEncoder.matches(form.getPw(), userEntity.getPw())) {
                if (form.getMpw().equals(form.getCpw())) {
                    userEntity.setPw(passwordEncoder.encode(form.getMpw()));
                    log.info("비밀번호 변경 완료");
                } else {
                    passwordError = true;
                    model.addAttribute("passwordError", "새 비밀번호가 일치하지 않습니다.");
                    log.info("새 비밀번호 불일치 에러");
                }
            } else {
                passwordError = true;
                model.addAttribute("passwordError", "현재 비밀번호가 일치하지 않습니다.");
                log.info("현재 비밀번호 불일치 에러");
            }
        }

        // 비밀번호 에러가 났을때 마이페이지를 리턴하는데, 사용자 정보를 다시 넣어놓지 않으면 null 오류가 난다
        if (passwordError) {
            model.addAttribute("loginInfo", userEntity.getId());
            model.addAttribute("nameInfo", userEntity.getName());
            model.addAttribute("userInterests", userInterests);
            log.info("비밀번호 에러 - /users/mypage 리턴");
            return "/users/mypage";
        }

        // 체크박스의 체크 유무에 따라 DB에 저장
        userInterests.setPolitics(form.getPolitics() != null);
        userInterests.setEconomy(form.getEconomy() != null);
        userInterests.setSociety(form.getSociety() != null);
        userInterests.setLifestyleCulture(form.getLifestyleCulture() != null);
        userInterests.setIt(form.getIt() != null);
        userInterests.setWorld(form.getWorld() != null);
        userInterests.setStock(form.getStock() != null);

        // 업데이트 된 엔티티 저장
        userInterestsRepository.save(userInterests);
        log.info("관심분야 업데이트 DB에 저장 완료");

        userRepository.save(userEntity);
        log.info("비밀번호 업데이트 DB에 저장 완료");

        return "redirect:/main";

    }

    /**
     * 회원탈퇴 처리
     * */
    @PostMapping("/users/delete")
    public String deleteUser(@AuthenticationPrincipal User user) {

        log.info("회원정보 삭제 요청");

        // 삭제 대상 가져오기
        UserInfo userEntity = userRepository.findByid(user.getUsername()).orElse(null);
        log.info("UserInfo 삭제 대상 가져오기 완료");
        UserInterests userInterests = userInterestsRepository.findById(user.getUsername()).orElse(null);
        log.info("UserInterests 삭제 대상 가져오기 완료");

        // 대상 엔티티 삭제
        userInterestsRepository.delete(Objects.requireNonNull(userInterests));
        userRepository.delete(Objects.requireNonNull(userEntity));

        return "redirect:/logout";
    }

}
