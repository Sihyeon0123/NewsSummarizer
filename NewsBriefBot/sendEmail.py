import smtplib  # SMTP 사용을 위한 모듈
import re  # Regular Expression을 활용하기 위한 모듈
from email.mime.multipart import MIMEMultipart  # 메일의 Data 영역의 메시지를 만드는 모듈
from email.mime.text import MIMEText  # 메일의 본문 내용을 만드는 모듈
from email.mime.image import MIMEImage  # 메일의 이미지 파일을 base64 형식으로 변환하기 위한 모듈
 
class SendEmail:
    def __init__(self) -> None:
        # smpt 서버와 연결
        self.gmail_smtp = "smtp.gmail.com"  # gmail smtp 주소
        self.gmail_port = 465  # gmail smtp 포트번호. 고정(변경 불가)
        self.smtp = None
        # 로그인
        self.my_account = "이메일 계정"
        self.my_password = "보낼 이메일 계정의 비밀번호"

    def sendEmail(self, addr = "아이디@naver.com", mail_title = "제목", mail_content = "안녕하세요!"):
        self.smtp = smtplib.SMTP_SSL(self.gmail_smtp, self.gmail_port)
        self.smtp.login(self.my_account, self.my_password)
        # 메일 기본 정보 설정
        msg = MIMEMultipart()
        msg["Subject"] = mail_title
        msg["From"] = self.my_account
        msg["To"] = addr
        
        content_part = MIMEText(mail_content, "plain")
        msg.attach(content_part)
 
        reg = "^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$"  # 유효성 검사를 위한 정규표현식
        if re.match(reg, addr):
            self.smtp.sendmail(self.my_account, addr, msg.as_string())
            print("정상적으로 메일이 발송되었습니다.")
        else:
            print("받으실 메일 주소를 정확히 입력하십시오.")
 
        # smtp 서버 연결 해제
        self.smtp.quit() 

if __name__ == "__main__":
    mail = SendEmail()
    mail.sendEmail()