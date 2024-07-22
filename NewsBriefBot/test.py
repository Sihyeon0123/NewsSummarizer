# 테스트 결과 쓰레드 생성에는 토큰소모 X
# 같은 쓰레드에 메시지를 추가하면 메시지가 계속 쌓여 토큰 소모량 증가할걸로 예상
# (토큰 소모량 체크를 하지는 않았지만 쓰레드 생성에 비용이 들지 않는다면 계속 새로운 쓰레드 생성하는 것이 유리)
#

# import embeddings
from openai import OpenAI
import time

apiKey = "sk-proj-bFdAZCjpZvMfz12bqquaT3BlbkFJEuFv7WSta3B859QfVrp0"
# 쓰레드 생성은 토큰 소모 X
client = OpenAI(api_key=apiKey)
news_thread = client.beta.threads.create()
ids = {'assistant_id': 'asst_3twHpxsoqsCeqUzu4QwJ6SYK', 'thread_id': f'{news_thread.id}'}


print("초기설정 완료", end="\n")

for i in range(1):
    print(i)
    msg = "애플의 새로운 인공지능(AI) 기능이 온디바이스(기기 자체적으로 AI를 구동하는 것) 서비스가 될 것으로 보인다. 애플이 다른 빅테크에 비해 뒤처진 AI에 온 힘을 쏟고 있는 가운데서다. 애플은 새로운 온디바이스 AI 서비스 일부 기능을 오는 6월 열리는 연례세계개발자컨퍼런스(WWDC)에서 공개할 예정이다.4월30일(현지시간) 파이낸셜타임스(FT)와 월스트리트저널(WSJ) 등 외신에 따르면 애플은 아이폰 등 모바일 기기에 자체 AI 서비스를 탑재하는 것에 집중하고 있다. 그동안 애플의 새로운 AI 서비스가 새로운 유형의 소프트웨어와 서비스가 될지 아니면 아이폰 등 애플 기기의 온디바이스 형태로 나타날지는 구체적으로 알려지지 않았는데 그 윤곽이 드러난 것이다.애플의 새 AI 서비스는 애플 하드웨어와 소프트웨어에서 실행될 수 있는 온디바이스 생성형 AI가 유력한 것으로 전해진다. 경쟁사인 삼성전자의 AI 스마트폰 갤럭시 S24 시리즈의 실시간 통역처럼 온디바이스 AI 환경에서 구연될 수 있는 AI 서비스와 유사한 개념이다.애플의 새 AI 서비스는 올해 가을에 공개될 아이폰16에 탑재될 가능성이 높다는 설명이다. 애플이 구상하고 있는 온디바이스 AI 서비스는 애플의 모든 앱과 상호작용할 수 있는 업그레이드된 '시리'를 포함해 음성으로 작동하는 스마트 개인 비서다.모건 스탠리의 애널리스트인 에릭 우드링은 \"일반 소비자들은 애플의 WWDC에서 게임 체인저가 될 수 있는 한두 가지 AI 기능의 프리뷰를 볼 수 있을 것\"이라고 내다봤다. 이와 관련 WSJ은 \"애플의 비즈니스 모델이 하드웨어 중심이기 때문에 온디바이스 AI가 매출에 더 큰 영향을 미칠 수 있다\"라고 진단했다.카네기멜론대에서 애플에 영입된 루슬란 살라쿠트디노프 전 교수는 \"애플이 기기에서 최대한 많은 일을 하는 것에 집중하고 있다\"라고 말했다. 이어 그는 \"애플은 AI 모델을 구동하는 데 필요한 방대한 양의 데이터를 처리할 수 있는 더 강력한 칩을 필요로 하고 있다\"라고 덧붙였다.애플이 온디바이스 AI 서비스를 아이폰에 탑재한다면 아이폰 판매를 늘리는데 도움이 될 것이라는 전망이 지배적이다. 애플은 오랫동안 프리미엄 휴대폰 시장을 지배했지만 현재 스마트폰 시장은 정체되고 있다. 소비자들의 휴대폰 교체시기가 늦어지고 있어서다. 비저블알파의 추정치에 따르면 전문가들은 올해 아이폰 판매량이 전년 에 비해 감소할 것으로 보고 있다. 애플이 AI에 절박한 이유다.현재 구글 AI를 총괄했던 존 지안난드레아를 비롯해 구글의 전직 핵심 인사들이 애플의 AI 팀으로 활동하면서 애플 온디바이스 AI를 구체화하고 있다는 것이 FT의 설명이다. 애플은 지난 2018년 최고 AI 임원으로 존 지아난드레아를 영입한 이후 경쟁사로부터 최소 36명의 전문가를 영입하는 등 구글 출신 인력을 타깃으로 삼았다.한편, 애플 최고경영자(CEO) 팀 쿡은 이미 수 차례 \"애플이 광범위한 AI 기술을 연구하고 있고 새로운 기술에 대해 책임감 있게 투자하고 혁신하고 있다\"라고 밝힌 바 있다."

    # 쓰레드에 메시지 추가 소모 X
    thread_message = client.beta.threads.messages.create(
        thread_id = ids['thread_id'],
        role="user", 
        content=msg,
    )
    print("thread_message:", thread_message, end="\n\n")

    # 메시지 실행 요청시 리퀘스트 횟수 +1
    run = client.beta.threads.runs.create(
        thread_id=ids['thread_id'],
        assistant_id=ids['assistant_id'],
        # max_completion_tokens=300
    )
    print("run:", run, end="\n\n")

    while True:
        time.sleep(3)
        run = client.beta.threads.runs.retrieve(
            thread_id=ids['thread_id'],
            run_id=run.id
        )
        if run.status == "completed":
            print("답변 받음")
            break
        elif run.status == "failed":    
            print("요청 다씀")
            time.sleep(60)
            run = client.beta.threads.runs.create(
                thread_id=ids['thread_id'],
                assistant_id=ids['assistant_id'],
            )
        else :
            print("작업중인듯?")

    # 메시지 받아옴 요청 횟수 X
    thread_message = client.beta.threads.messages.list(ids['thread_id'],)
    print("답변:", thread_message.data[0].content[0].text.value)
    print()
    print("쓰레드 메시지 목록 출력")

    for message in thread_message.data:
            print(message.content[0].text.value)

# em = embeddings.Embedding(apiKey=apiKey)
# embed = em.getEmbedding("테스트")
# print("\n임베딩 완료")

"""
# 초기상태
8 2280
9 27

애플의 새로운 인공지능(AI) 기능이 온디바이스(기기 자체적으로 AI를 구동하는 것) 서비스가 될 것으로 보인다. 애플이 다른 빅테크에 비해 뒤처진 AI에 온 힘을 쏟고 있는 가운데서다. 애플은 새로운 온디바이스 AI 서비스 일부 기능을 오는 6월 열리는 연례세계개발자컨퍼런스(WWDC)에서 공개할 예정이다.

# 1회 전송시
쓰레드를 생성하여 위의 문장만 1회 보냈을 때
9 2567(287토큰 사용)
9 27

# 같은 문장을 보내면 같은 토큰이 사용되는가??
10 2854(287토큰 사용 예상)
9 27

# 결과 (답변 토큰에 따라 달라지지만 거의 비슷)
10 2840(273토큰 사용)
9 27
 

# 2회 전송시
그럼 그냥 질문을 두번 보내면  574 토큰을 예상한다....
12 3414 (574토큰 언저리 예상)
9 27

# 결과
확실히 더 많이 소모되는 모습을 보임 (기존의 1회 질문에 1회 질문을 더 해 총 1, 2 -> 3번의 질문을 보낸것인가? 계산시
소모량은 273 * 1.5 = 409.5 로 실제 결과와 비슷한 모습을 보인다 )
12 3637(797, 1회당 398.5 사용 )
9 27


# 3회 전송시
1회에 273 예상시 273 + 546 + 819 = 1638 정도.. 
15 5275 (1638 토큰 예상, 1회에 546)
9 27

#결과
쓰레드에 메시지를 추가할 수록 토큰 소모량이 늘어난다..
15 5240
9 27 


# 뉴스 요약시 토큰 사용량
1회 요청 
1회 처리 상태 확인(처리중임을 확인함)
1회 답변
# 결과
16 6845(1605토큰 사용 답변은 약 150토큰 사용)
9 27

"""