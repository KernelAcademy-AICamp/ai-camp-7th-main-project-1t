"""
ORBIT - 한 줄 아이디어로 '함께할 팀원을 찾는 기획안'을 만들어 주는 프로그램

⭐ ORBIT의 핵심:
   ORBIT은 사업계획서를 만드는 서비스가 '아니라',
   "이 아이디어를 함께 만들 팀원을 찾아주는" 서비스입니다.
   그래서 결과에는 반드시 아래 두 가지가 들어갑니다:
     1. neededTeammates (필요한 팀원)   — 이 아이디어를 실현하려면 어떤 사람이 필요한가
     2. matchFactors    (매칭 중요 요소) — 실력 외에 어떤 성향·가치가 잘 맞아야 하는가

사용법:
    python src/main.py "페트병 뚜껑을 그립톡으로 재활용하는 사업"

아이디어가 너무 빈약하면(예: "그립톡 사업"), AI 가 기획안을 억지로 만들지 않고
'무엇을 더 알려달라'(askFor)고 되물어 줍니다.
"""

import json
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

# 1) .env 파일에 적어둔 ANTHROPIC_API_KEY 를 불러옵니다.
#    (코드 안에 키를 직접 쓰지 않아도 됩니다 — 그게 안전한 방법입니다.)
load_dotenv()

# 2) 키가 제대로 들어있는지 친절하게 확인해 줍니다.
if not os.getenv("ANTHROPIC_API_KEY") or "여기에" in os.getenv("ANTHROPIC_API_KEY", ""):
    raise SystemExit(
        "❌ .env 파일에 진짜 API 키가 아직 없습니다.\n"
        "   ORBIT/.env 를 열어 ANTHROPIC_API_KEY= 뒤에 키를 붙여넣어 주세요."
    )

# 3) Anthropic 클라이언트를 만듭니다. (.env 의 키를 자동으로 사용합니다.)
client = Anthropic()

# 4) Claude 에게 줄 '역할(시스템 프롬프트)'.
#    여기서 ORBIT 의 핵심 규칙과, 받아야 할 JSON 모양을 정확히 알려줍니다.
SYSTEM_PROMPT = """당신은 ORBIT의 기획안 생성 AI입니다.
사용자가 던진 한 줄 아이디어를, 함께 만들 팀원이 한눈에 이해하고 합류하고 싶게 만드는 '기획안 페이지'로 구체화합니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 앞뒤에 다른 말, 설명, 코드펜스(```)를 절대 붙이지 마세요.
- 어조: 각 분야 전문가가 읽고 '나도 이 프로젝트에 합류하고 싶다'고 느낄 만큼 설득력 있고 진정성 있게 씁니다.
  단, 아직 '아이디어 단계(진척도 0%)'이므로 없는 성과를 있는 척하거나 과장하지는 마세요.
- story(왜 이 사업을 하는가)는 아이디어 제공자가 1인칭('저는…')으로 들려주는 짧은 이야기 3개 문단입니다. 계기 → 발견 → 신념/다짐 흐름으로, 사람 냄새 나게.
- whyNow(왜 지금·왜 함께)는 지금 시작해야 하는 이유 3가지. 각 {icon(이모지 1개), title(짧게), desc(한 줄)}.
- productNote: 어떤 제품/서비스를 만드는지 한 줄 설명.
- neededTeammates(필요한 팀원)는 3~5명. 각 {role, detail, skills}.
    · role : 직무명(개발자)이 아니라 '무엇을 할 수 있는 사람'(폐플라스틱 가공 설비를 다룰 수 있는 사람)
    · detail : 합류하면 맡는 일과 왜 중요한지, 그 분야 사람이 끌릴 이유 한 줄
    · skills : 그 자리에 필요한 핵심 역량 태그 2~4개(짧은 명사, matchProfile.roleSkills와 같은 어휘). roleSkills 는 모든 팀원 skills 를 아우르는 합집합이어야 합니다.
- matchFactors(매칭 중요 요소): 실력 외에 이 팀에 맞으려면 중요한 성향·가치 정확히 3개.
- aiQuestions: 합류 지원자가 답할 질문 2개. 이 아이디어 적합성을 가릴 단답형(1~2문장으로 답할 수 있는 것).
- founderQuestion: 아이디어 제공자가 팀원에게 묻고 싶을 법한 추천 질문 1개(나중에 제공자가 직접 수정합니다).
- matchProfile: 전문가(팀원) 매칭 점수 계산에 쓰는 구조화 속성. 아래 '허용 값'에서만 고르세요.
    · roleSkills : 이 프로젝트에 필요한 핵심 역량 태그 3~6개(짧은 명사. 예: 프론트엔드, 디자인, 마케팅, 생산설비, 식품위생).
    · domains    : 프로젝트 분야. [복지, 교육, 반려동물, 지역 커뮤니티, 의료, ESG, 콘텐츠, 생산성] 중 1~2개.
    · natures    : 프로젝트 성격. [사회적 가치, 수익, 창업, 학습] 중 1~2개.
    · minWeeklyCapacity : 팀원에게 기대하는 최소 주당 투입. [주 2시간 이하, 주 5시간, 주 10시간, 주 20시간 이상] 중 하나.
    · meetingMode : 진행 방식. 온라인만으로 가능하면 "online_only", 오프라인이 필요하면 "offline_optional".
- 현실적이고 작게 시작할 수 있는 규모로, 모두 한국어로.

[정상 응답 JSON 형식]
{
  "serviceName": "서비스 이름(짧고 기억하기 쉽게)",
  "tagline": "한 줄 슬로건",
  "lead": "히어로에 들어갈 감성적인 소개 2~3문장",
  "story": ["1인칭 스토리 문단1", "문단2", "문단3"],
  "whyNow": [
    {"icon": "🌍", "title": "제목", "desc": "한 줄 설명"},
    {"icon": "🧩", "title": "제목", "desc": "한 줄 설명"},
    {"icon": "🚀", "title": "제목", "desc": "한 줄 설명"}
  ],
  "productNote": "어떤 제품/서비스를 만드는지 한 줄",
  "plan": {
    "problem": "어떤 문제를 푸는가",
    "solution": "어떻게 푸는가",
    "target": "누구를 위한 것인가",
    "revenue": "어떻게 돈을 버는가"
  },
  "neededTeammates": [
    {"role": "무엇을 할 수 있는 사람 1", "detail": "맡는 일과 끌리는 이유 한 줄", "skills": ["프론트엔드", "디자인"]},
    {"role": "무엇을 할 수 있는 사람 2", "detail": "맡는 일과 끌리는 이유 한 줄", "skills": ["마케팅"]},
    {"role": "무엇을 할 수 있는 사람 3", "detail": "맡는 일과 끌리는 이유 한 줄", "skills": ["운영", "고객관리"]}
  ],
  "matchFactors": ["성향·가치 1", "성향·가치 2", "성향·가치 3"],
  "aiQuestions": ["팀원이 답할 질문 1", "팀원이 답할 질문 2"],
  "founderQuestion": "제공자가 팀원에게 물을 추천 질문 1개",
  "matchProfile": {
    "roleSkills": ["프론트엔드", "디자인", "마케팅"],
    "domains": ["콘텐츠"],
    "natures": ["창업", "수익"],
    "minWeeklyCapacity": "주 10시간",
    "meetingMode": "online_only"
  },
  "needMoreInfo": false
}

[입력이 너무 빈약해서 기획안을 만들 수 없을 때 — 예: "그립톡 사업" 처럼 한두 단어]
{
  "needMoreInfo": true,
  "askFor": ["무엇을 재활용/활용하나요?", "누구에게 파나요?", "무엇이 강점인가요?"]
}"""


# 4-2) 발표 데모용 '등록된 팀원 풀' — 실제로는 가입한 사람들의 프로필이 들어올 자리입니다.
#      experts 스키마(테이블정의서 v0.2) 기준 필드로, 결정적 매칭 점수 계산에 그대로 쓰입니다.
TEAMMATE_POOL = [
    {"name": "김도현", "headline": "플라스틱 사출·금형을 직접 다루는 제조 엔지니어",
     "primaryRole": "생산설비·제조",
     "skills": "생산설비, 제조, 사출, 금형, 시제품",
     "traits": "직접 손으로 만들며 빠르게 검증하는 걸 즐김, 환경 문제에 진심",
     "interestDomains": ["ESG", "생산성"], "participationMotivation": ["창업 기회", "수익"],
     "weeklyCapacity": "주 20시간 이상", "contactHours": ["평일 저녁", "주말"], "collabMode": "수도권 오프라인 가능",
     "links": [{"label": "포트폴리오", "url": "https://notion.so/kimdohyun-portfolio"}],
     "bio": "폐플라스틱 재활용 설비를 직접 만들어 본 경험이 있어, 에코그립 양산 라인을 빠르게 세팅할 수 있어요."},
    {"name": "이서연", "headline": "브랜드·제품 디자이너",
     "primaryRole": "디자인",
     "skills": "디자인, 브랜딩, 패키지, 굿즈디자인",
     "traits": "미적 감각이 뛰어나고 트렌드에 민감, 작게 시작해 다듬는 걸 선호",
     "interestDomains": ["콘텐츠", "ESG"], "participationMotivation": ["포트폴리오", "창업 기회"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 저녁"], "collabMode": "온라인+화상",
     "links": [{"label": "포트폴리오", "url": "https://www.behance.net/leeseoyeon"}],
     "bio": "제품의 미적 완성도와 브랜드 무드를 함께 잡습니다. 굿즈·패키지 디자인이 강점이에요."},
    {"name": "박지훈", "headline": "SNS·콘텐츠 마케터",
     "primaryRole": "마케팅",
     "skills": "마케팅, SNS, 콘텐츠, 브랜드스토리텔링",
     "traits": "Gen Z 트렌드 이해도 높음, 가치소비·친환경 메시지에 공감",
     "interestDomains": ["콘텐츠", "ESG"], "participationMotivation": ["창업 기회", "네트워킹"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 저녁", "주말"], "collabMode": "온라인+화상",
     "links": [{"label": "인스타그램", "url": "https://instagram.com/parkjihoon.mkt"}],
     "bio": "작은 브랜드를 0에서 팬덤으로 키운 경험이 있어요. Gen Z 타깃 친환경 브랜딩에 강합니다."},
    {"name": "최민지", "headline": "B2B 제휴·영업 담당",
     "primaryRole": "영업·제휴",
     "skills": "영업, 제휴, B2B, 온라인판매",
     "traits": "사람 만나 발로 뛰는 걸 좋아함, 첫 매출을 만드는 데 집중",
     "interestDomains": ["생산성", "교육"], "participationMotivation": ["수익", "네트워킹"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮"], "collabMode": "전국 오프라인 가능"},
    {"name": "정우성", "headline": "웹·앱 풀스택 개발자",
     "primaryRole": "앱개발",
     "skills": "앱개발, 웹개발, 플랫폼, 결제시스템",
     "traits": "MVP를 빠르게 만들어 출시, 사용자 피드백으로 개선",
     "interestDomains": ["생산성", "반려동물"], "participationMotivation": ["창업 기회", "학습"],
     "weeklyCapacity": "주 20시간 이상", "contactHours": ["언제든"], "collabMode": "온라인만"},
    {"name": "한가람", "headline": "서비스 기획·운영 매니저",
     "primaryRole": "기획·운영",
     "skills": "기획, 운영, 프로세스설계, 고객응대",
     "traits": "꼼꼼하게 빈틈을 메우는 성향, 팀의 중심을 잡는 역할",
     "interestDomains": ["생산성", "교육"], "participationMotivation": ["사회적 가치", "학습"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮", "평일 저녁"], "collabMode": "온라인+화상"},
    {"name": "오은별", "headline": "식품 조리·위생 표준화 전문가",
     "primaryRole": "식품위생",
     "skills": "식품위생, HACCP, 레시피표준화, 제조",
     "traits": "맛과 안전을 둘 다 챙김, 정성스러운 손맛을 중시",
     "interestDomains": ["복지", "ESG"], "participationMotivation": ["사회적 가치", "수익"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮"], "collabMode": "수도권 오프라인 가능"},
    {"name": "강태현", "headline": "시니어 대상 교육·오프라인 운영 경험자",
     "primaryRole": "교육·운영",
     "skills": "교육, 오프라인운영, 커뮤니케이션, 제휴영업",
     "traits": "참을성 있고 사람을 편안하게 해줌, 사회적 가치를 중시",
     "interestDomains": ["교육", "복지"], "participationMotivation": ["사회적 가치", "네트워킹"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮", "주말"], "collabMode": "전국 오프라인 가능"},
    {"name": "윤채원", "headline": "사용자 경험을 설계하는 프론트엔드 개발자",
     "primaryRole": "프론트엔드",
     "skills": "프론트엔드, React, UIUX, 플랫폼",
     "traits": "작은 인터랙션까지 다듬는 걸 즐김, 사용자 관점으로 사고",
     "interestDomains": ["콘텐츠", "생산성"], "participationMotivation": ["포트폴리오", "학습"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 저녁"], "collabMode": "온라인만"},
    {"name": "배준호", "headline": "확장 가능한 서버를 만드는 백엔드 개발자",
     "primaryRole": "백엔드",
     "skills": "백엔드, API연동, 결제시스템, 플랫폼",
     "traits": "안정성과 구조를 중시, 문제를 근본부터 파고듦",
     "interestDomains": ["생산성", "의료"], "participationMotivation": ["창업 기회", "수익"],
     "weeklyCapacity": "주 20시간 이상", "contactHours": ["언제든"], "collabMode": "온라인만"},
    {"name": "서지우", "headline": "0에서 앱을 출시해본 모바일 개발자",
     "primaryRole": "앱개발",
     "skills": "앱개발, 플랫폼, 결제시스템, 프론트엔드",
     "traits": "빠르게 만들어 검증, 출시 경험 다수",
     "interestDomains": ["반려동물", "지역 커뮤니티"], "participationMotivation": ["창업 기회", "학습"],
     "weeklyCapacity": "주 20시간 이상", "contactHours": ["평일 저녁", "주말"], "collabMode": "온라인+화상"},
    {"name": "임하늘", "headline": "데이터로 의사결정을 돕는 분석가",
     "primaryRole": "데이터",
     "skills": "데이터분석, SQL, 데이터시각화, 머신러닝",
     "traits": "숫자 뒤의 맥락을 읽음, 가설 검증을 좋아함",
     "interestDomains": ["의료", "생산성"], "participationMotivation": ["학습", "수익"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮"], "collabMode": "온라인+화상"},
    {"name": "노아름", "headline": "브랜드 무드를 만드는 UIUX 디자이너",
     "primaryRole": "디자인",
     "skills": "디자인, UIUX, 브랜딩, 그래픽",
     "traits": "감각과 논리를 함께, 트렌드에 민감",
     "interestDomains": ["콘텐츠", "교육"], "participationMotivation": ["포트폴리오", "네트워킹"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 저녁"], "collabMode": "온라인+화상"},
    {"name": "곽태민", "headline": "제품을 담는 패키지·굿즈 디자이너",
     "primaryRole": "디자인",
     "skills": "디자인, 패키지, 굿즈디자인, 그래픽",
     "traits": "손에 잡히는 결과물을 좋아함, 디테일에 강함",
     "interestDomains": ["ESG", "콘텐츠"], "participationMotivation": ["포트폴리오", "창업 기회"],
     "weeklyCapacity": "주 5시간", "contactHours": ["주말"], "collabMode": "수도권 오프라인 가능"},
    {"name": "신유진", "headline": "영상으로 이야기를 전하는 크리에이터",
     "primaryRole": "디자인",
     "skills": "영상편집, 콘텐츠, 그래픽",
     "traits": "스토리텔링에 강함, 빠른 제작 가능",
     "interestDomains": ["콘텐츠", "교육"], "participationMotivation": ["포트폴리오", "수익"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 저녁", "주말"], "collabMode": "온라인만"},
    {"name": "문지호", "headline": "숫자로 성장을 만드는 퍼포먼스 마케터",
     "primaryRole": "마케팅",
     "skills": "마케팅, 퍼포먼스마케팅, SNS, 콘텐츠",
     "traits": "데이터 기반으로 실험, ROAS에 집착",
     "interestDomains": ["콘텐츠", "생산성"], "participationMotivation": ["수익", "네트워킹"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮", "평일 저녁"], "collabMode": "온라인만"},
    {"name": "조은서", "headline": "마음을 움직이는 카피라이터",
     "primaryRole": "마케팅",
     "skills": "카피라이팅, 콘텐츠, 브랜드스토리텔링",
     "traits": "한 문장에 진심을 담음, 브랜드 톤을 잘 잡음",
     "interestDomains": ["콘텐츠", "복지"], "participationMotivation": ["포트폴리오", "사회적 가치"],
     "weeklyCapacity": "주 5시간", "contactHours": ["평일 저녁"], "collabMode": "온라인+화상"},
    {"name": "백승우", "headline": "첫 매출을 만드는 세일즈 리드",
     "primaryRole": "영업·제휴",
     "skills": "영업, 제휴, B2B, 온라인판매",
     "traits": "거절을 두려워 않음, 관계를 오래 이어감",
     "interestDomains": ["생산성", "지역 커뮤니티"], "participationMotivation": ["수익", "네트워킹"],
     "weeklyCapacity": "주 20시간 이상", "contactHours": ["평일 낮"], "collabMode": "전국 오프라인 가능"},
    {"name": "홍세라", "headline": "구독 커머스를 굴려본 운영자",
     "primaryRole": "영업·제휴",
     "skills": "구독커머스, 온라인판매, 운영, 공급망",
     "traits": "반복 구매 구조를 설계, 고객 유지에 강함",
     "interestDomains": ["복지", "생산성"], "participationMotivation": ["수익", "창업 기회"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮", "평일 저녁"], "collabMode": "온라인+화상"},
    {"name": "남기훈", "headline": "공급망과 물류를 짜는 SCM 담당",
     "primaryRole": "영업·제휴",
     "skills": "공급망, 제휴, 운영, 자재구매",
     "traits": "비용과 리드타임을 최적화, 꼼꼼함",
     "interestDomains": ["생산성", "ESG"], "participationMotivation": ["수익", "학습"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮"], "collabMode": "수도권 오프라인 가능"},
    {"name": "구본영", "headline": "현장을 아는 생산설비 엔지니어",
     "primaryRole": "제조·생산",
     "skills": "생산설비, 제조, 사출, 품질관리",
     "traits": "현장 문제 해결에 강함, 손이 빠름",
     "interestDomains": ["ESG", "생산성"], "participationMotivation": ["창업 기회", "수익"],
     "weeklyCapacity": "주 20시간 이상", "contactHours": ["평일 저녁", "주말"], "collabMode": "전국 오프라인 가능",
     "links": [{"label": "작업 사례", "url": "https://behance.net/gubonyoung"}],
     "bio": "소규모 친환경 제품 양산 라인을 여러 번 구축했습니다. 초기 시제품부터 함께 만들고 싶어요."},
    {"name": "양수빈", "headline": "품질을 지키는 QA·품질관리자",
     "primaryRole": "제조·생산",
     "skills": "품질관리, 제조, 프로세스설계",
     "traits": "기준을 세우고 지킴, 재발 방지에 집중",
     "interestDomains": ["의료", "생산성"], "participationMotivation": ["학습", "수익"],
     "weeklyCapacity": "주 5시간", "contactHours": ["평일 낮"], "collabMode": "수도권 오프라인 가능"},
    {"name": "전하람", "headline": "안전한 먹거리를 만드는 식품 전문가",
     "primaryRole": "식품·위생",
     "skills": "식품위생, HACCP, 레시피표준화, 소량생산·포장",
     "traits": "맛과 안전을 함께, 표준화에 능함",
     "interestDomains": ["복지", "ESG"], "participationMotivation": ["사회적 가치", "수익"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮", "주말"], "collabMode": "수도권 오프라인 가능"},
    {"name": "손예린", "headline": "눈높이로 가르치는 교육 콘텐츠 기획자",
     "primaryRole": "교육·운영",
     "skills": "교육, 커리큘럼설계, 콘텐츠",
     "traits": "배우는 사람 입장에서 설계, 인내심 강함",
     "interestDomains": ["교육", "복지"], "participationMotivation": ["사회적 가치", "포트폴리오"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 저녁"], "collabMode": "온라인+화상"},
    {"name": "고재원", "headline": "오프라인 공간을 굴리는 운영 매니저",
     "primaryRole": "교육·운영",
     "skills": "오프라인운영, 운영, 커뮤니케이션, 제휴영업",
     "traits": "현장을 매끄럽게, 사람을 편하게 함",
     "interestDomains": ["지역 커뮤니티", "교육"], "participationMotivation": ["네트워킹", "사회적 가치"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮", "주말"], "collabMode": "전국 오프라인 가능"},
    {"name": "류지안", "headline": "서비스를 설계하는 프로덕트 매니저",
     "primaryRole": "기획·운영",
     "skills": "기획, PM, 사업기획, 프로세스설계",
     "traits": "큰 그림과 우선순위를 잡음, 실행까지 챙김",
     "interestDomains": ["생산성", "의료"], "participationMotivation": ["창업 기회", "학습"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 저녁"], "collabMode": "온라인만"},
    {"name": "심우재", "headline": "빈틈을 메우는 운영·CS 매니저",
     "primaryRole": "기획·운영",
     "skills": "운영, 고객응대, 프로세스설계",
     "traits": "꼼꼼하게 챙김, 고객의 목소리를 중시",
     "interestDomains": ["복지", "생산성"], "participationMotivation": ["사회적 가치", "학습"],
     "weeklyCapacity": "주 5시간", "contactHours": ["평일 낮", "평일 저녁"], "collabMode": "온라인+화상"},
    {"name": "표민경", "headline": "반려동물 서비스를 기획하는 운영자",
     "primaryRole": "기획·운영",
     "skills": "기획, 운영, 커뮤니티, 마케팅",
     "traits": "반려동물에 진심, 커뮤니티 운영 감각",
     "interestDomains": ["반려동물", "지역 커뮤니티"], "participationMotivation": ["창업 기회", "네트워킹"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 저녁", "주말"], "collabMode": "온라인+화상"},
    {"name": "안소정", "headline": "지역과 사람을 잇는 커뮤니티 매니저",
     "primaryRole": "교육·운영",
     "skills": "커뮤니티, 운영, 오프라인운영, 콘텐츠",
     "traits": "동네 단위로 신뢰를 쌓음, 따뜻함",
     "interestDomains": ["지역 커뮤니티", "복지"], "participationMotivation": ["사회적 가치", "네트워킹"],
     "weeklyCapacity": "주 5시간", "contactHours": ["주말"], "collabMode": "수도권 오프라인 가능"},
    {"name": "하동욱", "headline": "헬스케어 도메인을 아는 기획자",
     "primaryRole": "기획·운영",
     "skills": "기획, 데이터분석, 사업기획",
     "traits": "의료 규제와 사용자 니즈를 함께 봄",
     "interestDomains": ["의료", "생산성"], "participationMotivation": ["학습", "창업 기회"],
     "weeklyCapacity": "주 10시간", "contactHours": ["평일 낮"], "collabMode": "온라인+화상"},

    # ── 라이더 중 '투자자'(kind: investor) — 스킬이 아닌 '관심 분야'로 매칭한다 ──
    {"name": "정민석", "headline": "초기 스타트업에 베팅하는 엔젤 투자자", "kind": "investor",
     "traits": "될성부른 팀에 먼저 투자, 실행력 있는 창업자를 선호",
     "interestDomains": ["ESG", "콘텐츠"], "investStage": "시드", "investTicket": "3천만~1억",
     "portfolio": ["리필리(시드)", "제로마켓(시드)", "그립플레이(엔젤)"],
     "investStyle": "리드·팔로우 모두", "decisionSpeed": "2~3주",
     "support": ["초기 브랜딩", "네트워크 연결", "IR 코칭"],
     "links": [{"label": "투자 이력(AngelList)", "url": "https://angel.co/jungminseok"}],
     "bio": "ESG·콘텐츠 초기 스타트업을 주로 봅니다. 자금 외에 초기 브랜딩·네트워크 연결도 돕습니다."},
    {"name": "한서영", "headline": "프리A 라운드를 보는 초기 VC 심사역", "kind": "investor",
     "traits": "시장 크기와 팀을 함께 봄, 데이터로 성장을 검증",
     "interestDomains": ["생산성", "의료"], "investStage": "프리A", "investTicket": "1억~5억",
     "portfolio": ["헬스노트(프리A)", "워크플로우(시리즈A)"],
     "investStyle": "팔로우 위주", "decisionSpeed": "3~4주",
     "support": ["후속 라운드 소개", "채용 연결", "지표 코칭"],
     "links": [{"label": "회사 소개", "url": "https://ventures.example.com"}],
     "bio": "지표로 성장을 검증하는 팀을 선호합니다. 후속 라운드 투자자 연결을 지원합니다."},
    {"name": "오세훈", "headline": "수익과 임팩트를 함께 보는 임팩트 투자자", "kind": "investor",
     "traits": "사회적 가치와 지속가능성을 중시, 지역·복지에 관심",
     "interestDomains": ["복지", "교육"], "investStage": "시드", "investTicket": "2천만~5천만",
     "portfolio": ["돌봄이음(시드)", "배움나눔(시드)"],
     "investStyle": "리드 투자", "decisionSpeed": "약 1개월",
     "support": ["임팩트 측정", "지역 파트너십", "정부지원 연계"],
     "links": [{"label": "임팩트 펀드 소개", "url": "https://impact.example.org"}],
     "bio": "수익과 사회적 임팩트를 함께 봅니다. 지역·복지 파트너십 연결에 강점이 있어요."},
]

# 4-3) 매칭 AI 의 역할(시스템 프롬프트).
MATCH_SYSTEM_PROMPT = """당신은 ORBIT의 팀원 매칭 AI입니다.
주어진 '사업 기획안'과 '등록된 팀원 풀'을 보고, 이 아이디어를 함께 만들기에 가장 잘 맞는 팀원을 골라줍니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 외 다른 말이나 코드펜스(```)를 절대 붙이지 마세요.
- 반드시 '등록된 팀원 풀' 안에 실제로 있는 사람(name)만 추천하세요. 없는 사람을 지어내지 마세요.
- 정말 잘 맞는 사람만 2~4명 고르세요. 억지로 채우지 마세요.
- 각 추천에는 그 사람이 기획안의 어떤 '필요한 팀원' 역할을 채우는지(fitsRole)와,
  왜 이 아이디어/팀 분위기에 잘 맞는지(reason)를 구체적으로 적으세요.
- fitLevel 은 "높음" 또는 "보통" 중 하나로 적으세요.
- 모든 내용은 한국어로.

[응답 JSON 형식]
{
  "matches": [
    {"name": "팀원 이름", "fitsRole": "채우는 역할", "fitLevel": "높음", "reason": "왜 잘 맞는지 구체적으로"}
  ]
}"""


# 4-4) 합류 질문 추천 AI 의 역할 — 아이디어 제공자가 기획서를 만들 때 보여줄 질문 후보를 만듭니다.
QUESTION_SYSTEM_PROMPT = """당신은 ORBIT의 '합류 질문 추천 AI'입니다.
아이디어 제공자가 합류 지원자를 가릴 수 있도록, 이 프로젝트에 꼭 맞는 사람인지 판별하는 좋은 질문을 추천합니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 외 다른 말이나 코드펜스(```)를 절대 붙이지 마세요.
- aiQuestionCandidates: 지원자의 역량·상황·의지를 가릴 수 있는, 1~2문장으로 답할 수 있는 단답형 질문 4개.
- founderQuestionSuggestions: 아이디어 제공자가 직접 묻고 싶어할 만한 질문 추천 3개 (시간 약속, 합류 동기, 가치관 등).
- 모두 한국어로, 짧고 명확하게.

[응답 JSON 형식]
{
  "aiQuestionCandidates": ["질문1", "질문2", "질문3", "질문4"],
  "founderQuestionSuggestions": ["질문1", "질문2", "질문3"]
}"""

# 4-5) 합류 적합도(매칭률) 평가 AI 의 역할.
JOIN_SYSTEM_PROMPT = """당신은 ORBIT의 '합류 적합도 평가 AI'입니다.
합류 지원자의 프로필과, 이 프로젝트의 기획안·매칭 요소·필수 질문을 보고,
지원자가 각 질문에 어떻게 답할지 추정한 뒤, 프로젝트와 얼마나 잘 맞는지 매칭률(0~100%)을 매깁니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 외 다른 말이나 코드펜스(```)를 절대 붙이지 마세요.
- answers: 주어진 필수 질문 각각에 대해, 이 지원자라면 줄 법한 1~2문장 답변(answer)과 그 답이 적합한지 한 줄 코멘트(comment).
- bestRole: 기획안의 neededTeammates(필요 팀원) 중, 이 지원자의 이력서(skills·traits)에 가장 잘 맞는 자리 하나를 골라 그 role 문구를 그대로 적으세요. 지원자 역량과 동떨어진 자리를 고르지 마세요.
- fitItems: 이 팀과의 궁합을 보여주는 항목 3개. 각 {title, desc, level}. level 은 "잘 맞음" / "정확" / "보통" 중 하나이며, 솔직하게 약점("보통")도 하나 포함하세요.
- matchRate: 0~100 사이 정수. 기획안의 matchFactors(성향·가치)와 neededTeammates(필요 역량)를 지원자 이력서가 얼마나 충족하는지 근거 있게 판단하세요. 과장하지 마세요.
- verdict: "강력 추천" / "추천" / "보류" 중 하나.
- summary: 매칭 결과를 한 줄로 요약.
- 모두 한국어로.

[응답 JSON 형식]
{
  "answers": [
    {"question": "질문", "answer": "지원자의 예상 답변", "comment": "적합성 코멘트"}
  ],
  "bestRole": "이 지원자에게 가장 잘 맞는 자리(neededTeammates 중 하나)",
  "fitItems": [
    {"title": "환경 마인드", "desc": "제공자 핵심 가치와 정확히 일치", "level": "잘 맞음"},
    {"title": "필요 역량", "desc": "1순위 역할과 맞물림", "level": "정확"},
    {"title": "다른 감각", "desc": "다른 팀원과 보완하면 충분", "level": "보통"}
  ],
  "matchRate": 87,
  "verdict": "추천",
  "summary": "한 줄 요약"
}"""


# 4-6) 보충 질문 AI 의 역할 — 한 줄 아이디어를 또렷하게 만들 객관식 질문 2개.
BOOST_SYSTEM_PROMPT = """당신은 ORBIT의 '보충 질문 AI'입니다.
한 줄 아이디어를 더 또렷한 기획안으로 만들기 위해, 제공자에게 물을 객관식 질문 2개를 만듭니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 외 다른 말이나 코드펜스(```)를 절대 붙이지 마세요.
- 1번 질문은 '누가 가장 사고 싶어 할까/이용할까'(타겟), 2번은 '가장 중요한 강점은'을 묻습니다.
- 각 질문에 이 아이디어에 맞는 선택지 2개씩 제시합니다.
- 한국어로 짧고 명확하게.

[응답 JSON 형식]
{
  "questions": [
    {"q": "누가 가장 사고 싶어 할까요?", "options": ["선택지 A", "선택지 B"]},
    {"q": "가장 중요한 강점은요?", "options": ["선택지 A", "선택지 B"]}
  ]
}"""


# 4-7) 응답 스키마 — 구조화 출력(structured output)으로 AI가 항상 유효한 JSON만 내게 강제합니다.
#      (story 같은 긴 글에 따옴표가 들어가도 JSON이 깨지지 않습니다.)
def _obj(props, required):
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}

VISION_SCHEMA = _obj({
    "serviceName": {"type": "string"},
    "tagline": {"type": "string"},
    "lead": {"type": "string"},
    "story": {"type": "array", "items": {"type": "string"}},
    "whyNow": {"type": "array", "items": _obj(
        {"icon": {"type": "string"}, "title": {"type": "string"}, "desc": {"type": "string"}},
        ["icon", "title", "desc"])},
    "productNote": {"type": "string"},
    "plan": _obj(
        {"problem": {"type": "string"}, "solution": {"type": "string"},
         "target": {"type": "string"}, "revenue": {"type": "string"}},
        ["problem", "solution", "target", "revenue"]),
    "neededTeammates": {"type": "array", "items": _obj(
        {"role": {"type": "string"}, "detail": {"type": "string"},
         "skills": {"type": "array", "items": {"type": "string"}}}, ["role", "detail", "skills"])},
    "matchFactors": {"type": "array", "items": {"type": "string"}},
    "aiQuestions": {"type": "array", "items": {"type": "string"}},
    "founderQuestion": {"type": "string"},
    "matchProfile": _obj({
        "roleSkills": {"type": "array", "items": {"type": "string"}},
        "domains": {"type": "array", "items": {"type": "string"}},
        "natures": {"type": "array", "items": {"type": "string"}},
        "minWeeklyCapacity": {"type": "string"},
        "meetingMode": {"type": "string"},
    }, ["roleSkills", "domains", "natures", "minWeeklyCapacity", "meetingMode"]),
}, ["serviceName", "tagline", "lead", "story", "whyNow", "productNote",
    "plan", "neededTeammates", "matchFactors", "aiQuestions", "founderQuestion", "matchProfile"])

BOOST_SCHEMA = _obj({
    "questions": {"type": "array", "items": _obj(
        {"q": {"type": "string"}, "options": {"type": "array", "items": {"type": "string"}}},
        ["q", "options"])},
}, ["questions"])

MATCH_SCHEMA = _obj({
    "matches": {"type": "array", "items": _obj(
        {"name": {"type": "string"}, "fitsRole": {"type": "string"},
         "fitLevel": {"type": "string"}, "reason": {"type": "string"}},
        ["name", "fitsRole", "fitLevel", "reason"])},
}, ["matches"])

JOIN_SCHEMA = _obj({
    "answers": {"type": "array", "items": _obj(
        {"question": {"type": "string"}, "answer": {"type": "string"}, "comment": {"type": "string"}},
        ["question", "answer", "comment"])},
    "bestRole": {"type": "string"},
    "fitItems": {"type": "array", "items": _obj(
        {"title": {"type": "string"}, "desc": {"type": "string"}, "level": {"type": "string"}},
        ["title", "desc", "level"])},
    "matchRate": {"type": "integer"},
    "verdict": {"type": "string"},
    "summary": {"type": "string"},
}, ["answers", "bestRole", "fitItems", "matchRate", "verdict", "summary"])


def _extract_json(raw: str) -> dict:
    """AI 답변 문자열에서 JSON 부분만 안전하게 뽑아 dict 로 만듭니다.
    혹시 ```json 펜스나 앞뒤 잡설이 붙어 와도 견디도록 처리합니다."""
    text = raw.strip()
    # 코드펜스(```json ... ```)가 붙어 오면 제거
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    # 그래도 앞뒤에 글자가 있으면, 첫 '{' 부터 마지막 '}' 까지만 잘라서 파싱
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    # strict=False: 문자열 값 안에 줄바꿈 같은 제어문자가 있어도 견디게 파싱
    return json.loads(text, strict=False)


def generate_vision(idea: str, target_answer: str = "", strength_answer: str = "") -> dict:
    """한 줄 아이디어(+선택 보충답변)를 받아 기획안(dict)을 만들어 돌려줍니다."""
    user_prompt = (
        "다음 아이디어로 기획안을 만들어주세요.\n\n"
        f"[아이디어]\n{idea}\n\n"
        "[보충 답변]\n"
        f"- 가장 사고 싶어 할/이용할 사람: {target_answer or '(아직 없음)'}\n"
        f"- 가장 중요한 강점: {strength_answer or '(아직 없음)'}\n\n"
        "위에서 정한 JSON 형식으로만 답하세요."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",  # 속도·비용·품질 균형이 좋은 모델 (Opus보다 약 1.6배 저렴)
        max_tokens=3000,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": VISION_SCHEMA}},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = "".join(block.text for block in response.content if block.type == "text")
    return _extract_json(raw)


def generate_boost_questions(idea: str) -> dict:
    """한 줄 아이디어를 또렷하게 만들 보충 질문 2개(객관식)를 생성합니다."""
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=600,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": BOOST_SCHEMA}},
        system=BOOST_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"아이디어: {idea}\n\n보충 질문 2개를 JSON으로 만들어 주세요."}],
    )
    raw = "".join(b.text for b in response.content if b.type == "text")
    return _extract_json(raw)


def _fit_level(score: int, hard_pass: bool) -> str:
    """결정적 점수 → 표시용 적합도 등급."""
    if not hard_pass:
        return "보류"
    return "높음" if score >= 70 else "보통"


def _match_teammates_ai(vision: dict, needed: list) -> dict:
    """폴백 — matchProfile 이 없는 기획안은 기존처럼 AI 가 풀에서 직접 고릅니다."""
    vision_brief = {
        "serviceName": vision.get("serviceName"),
        "oneLineDesc": vision.get("oneLineDesc"),
        "neededTeammates": needed,
        "matchFactors": vision.get("matchFactors", []),
    }
    user_prompt = (
        "[사업 기획안]\n"
        f"{json.dumps(vision_brief, ensure_ascii=False, indent=2)}\n\n"
        "[등록된 팀원 풀]\n"
        f"{json.dumps([p for p in TEAMMATE_POOL if p.get('kind') != 'investor'], ensure_ascii=False, indent=2)}\n\n"
        "위 팀원 풀 안에서 이 아이디어에 가장 잘 맞는 사람을 골라 JSON 형식으로 답하세요."
    )
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1500,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": MATCH_SCHEMA}},
        system=MATCH_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = "".join(block.text for block in response.content if block.type == "text")
    return _extract_json(raw)


def compute_investor_score(investor: dict, project: dict) -> dict:
    """투자자 라이더는 스킬 대신 '관심 분야' 겹침으로 적합도를 계산한다."""
    mp = project or {}
    p_domains = _as_tokens(mp.get("domains"))
    e_domains = _as_tokens(investor.get("interestDomains"))
    m_dom = _overlap(p_domains, e_domains)
    ratio = (len(m_dom) / len(p_domains)) if p_domains else 1.0
    score = round(100 * ratio)
    return {
        "score": int(score),
        "hardPass": True,
        "hardReasons": [],
        "components": [
            {"key": "관심 분야", "weight": 100, "got": round(100 * ratio, 1),
             "pct": round(ratio * 100), "detail": f"겹친 분야: {', '.join(m_dom) or '없음'}"}
        ],
    }


def _match_entry(person: dict, bd: dict, fits_role: str, reason: str) -> dict:
    """추천 카드에 필요한 정보를 담아 매칭 결과 항목을 만든다(팀원/투자자 공통)."""
    kind = person.get("kind", "teammate")
    entry = {
        "name": person["name"],
        "kind": kind,
        "headline": person.get("headline", ""),
        "traits": person.get("traits", ""),
        "interestDomains": person.get("interestDomains", []),
        "links": person.get("links", []),
        "bio": person.get("bio", ""),
        "fitsRole": fits_role,
        "fitLevel": _fit_level(bd["score"], bd["hardPass"]),
        "reason": reason,
        "score": bd["score"],
        "breakdown": bd,
    }
    if kind == "investor":
        entry["investStage"] = person.get("investStage", "")
        entry["investTicket"] = person.get("investTicket", "")
        entry["portfolio"] = person.get("portfolio", [])
        entry["investStyle"] = person.get("investStyle", "")
        entry["decisionSpeed"] = person.get("decisionSpeed", "")
        entry["support"] = person.get("support", [])
    else:
        entry["skills"] = person.get("skills", "")
        entry["weeklyCapacity"] = person.get("weeklyCapacity", "")
        entry["collabMode"] = person.get("collabMode", "")
        entry["participationMotivation"] = person.get("participationMotivation", [])
        entry["contactHours"] = person.get("contactHours", [])
    return entry


def match_teammates(vision: dict) -> dict:
    """등록된 라이더 풀을 기획안과 비교해 추천 팀원(+관심 가질 만한 투자자)을 돌려줍니다.

    - 팀원: 결정적 점수(기술40·관심30·목적20·시간10+하드필터)로 랭킹·등급을 확정하고,
      AI 는 상위 후보의 '맡을 자리(fitsRole)'와 '추천 이유'만 씁니다.
    - 투자자(kind=investor): 스킬이 아닌 '관심 분야' 겹침으로 점수를 매겨, 분야가 맞는
      투자자만 추천 목록 뒤에 덧붙입니다(fitsRole='투자·자문').
    """
    needed = [t["role"] for t in vision.get("neededTeammates", [])]
    match_profile = vision.get("matchProfile")
    if not match_profile:
        return _match_teammates_ai(vision, needed)

    teammates = [p for p in TEAMMATE_POOL if p.get("kind") != "investor"]
    investors = [p for p in TEAMMATE_POOL if p.get("kind") == "investor"]

    # 1) 팀원: 결정적 점수 → 하드필터 통과 우선, 점수 내림차순 랭킹
    scored = [{"person": p, "bd": compute_match_score(p, match_profile)} for p in teammates]
    scored.sort(key=lambda s: (s["bd"]["hardPass"], s["bd"]["score"]), reverse=True)
    passing = [s for s in scored if s["bd"]["hardPass"]]
    top = (passing or scored)[:4]

    # 2) 상위 후보의 fitsRole·reason 만 AI 로 생성(점수는 이미 확정값)
    cand = [{
        "name": s["person"]["name"],
        "headline": s["person"].get("headline", ""),
        "skills": s["person"].get("skills", ""),
        "score": s["bd"]["score"],
        "scoreDetail": [f'{c["key"]} {c["got"]}/{c["weight"]}' for c in s["bd"]["components"]],
    } for s in top]
    user_prompt = (
        "[사업 기획안]\n"
        f"{json.dumps({'serviceName': vision.get('serviceName'), 'neededTeammates': needed, 'matchFactors': vision.get('matchFactors', [])}, ensure_ascii=False, indent=2)}\n\n"
        "[점수 상위 후보 — score 는 이미 확정된 값입니다]\n"
        f"{json.dumps(cand, ensure_ascii=False, indent=2)}\n\n"
        "각 후보마다 fitsRole(neededTeammates 중 가장 잘 맞는 자리 하나)과 "
        "reason(score·scoreDetail 과 모순 없는 추천 이유 한 줄)을 JSON 으로 작성하세요. "
        "score 는 절대 바꾸지 마세요."
    )
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1200,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": MATCH_SCHEMA}},
        system=MATCH_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = "".join(b.text for b in response.content if b.type == "text")
    ai_by_name = {m.get("name"): m for m in _extract_json(raw).get("matches", [])}

    # 3) 결정적 점수를 진실원천으로 병합
    matches = [
        _match_entry(
            s["person"], s["bd"],
            fits_role=ai_by_name.get(s["person"]["name"], {}).get("fitsRole") or (needed[0] if needed else ""),
            reason=ai_by_name.get(s["person"]["name"], {}).get("reason") or "",
        )
        for s in top
    ]
    matches.sort(key=lambda m: m["score"], reverse=True)

    # 4) 투자자: 관심 분야 점수로 겹치는 사람만 목록 뒤에 추가
    inv_scored = [{"person": p, "bd": compute_investor_score(p, match_profile)} for p in investors]
    inv_scored.sort(key=lambda s: s["bd"]["score"], reverse=True)
    for s in inv_scored:
        if s["bd"]["score"] <= 0:
            continue
        doms = ", ".join(_overlap(_as_tokens(match_profile.get("domains")),
                                  _as_tokens(s["person"].get("interestDomains")))) or "관심 분야"
        matches.append(_match_entry(
            s["person"], s["bd"], fits_role="투자·자문",
            reason=f"관심 분야({doms})가 맞아 초기 투자·자문에 관심을 가질 수 있어요.",
        ))
    return {"matches": matches}


def list_riders() -> dict:
    """등록된 라이더(팀원+투자자) 풀을 둘러보기용 카드 정보로 돌려준다."""
    riders = []
    for p in TEAMMATE_POOL:
        kind = p.get("kind", "teammate")
        r = {"name": p["name"], "kind": kind, "headline": p.get("headline", ""),
             "traits": p.get("traits", ""), "interestDomains": p.get("interestDomains", []),
             "links": p.get("links", []), "bio": p.get("bio", "")}
        if kind == "investor":
            r["investStage"] = p.get("investStage", "")
            r["investTicket"] = p.get("investTicket", "")
            r["portfolio"] = p.get("portfolio", [])
            r["investStyle"] = p.get("investStyle", "")
            r["decisionSpeed"] = p.get("decisionSpeed", "")
            r["support"] = p.get("support", [])
        else:
            r["primaryRole"] = p.get("primaryRole", "")
            r["skills"] = p.get("skills", "")
            r["weeklyCapacity"] = p.get("weeklyCapacity", "")
            r["collabMode"] = p.get("collabMode", "")
            r["participationMotivation"] = p.get("participationMotivation", [])
            r["contactHours"] = p.get("contactHours", [])
        riders.append(r)
    return {"riders": riders}


def print_matches(matches: dict) -> None:
    """매칭된 팀원을 보기 좋게 출력합니다."""
    found = matches.get("matches", [])
    print("\n🔗 ORBIT이 찾은 합류 추천 팀원 (등록된 8명 중에서)")
    print("=" * 60)
    if not found:
        print("   아직 딱 맞는 팀원이 없어요. (팀원 풀을 더 넓혀보세요)")
        print("=" * 60)
        return
    for person in found:
        star = "⭐⭐⭐" if person.get("fitLevel") == "높음" else "⭐⭐"
        print(f"   {star} {person['name']} — 매칭도: {person.get('fitLevel', '?')}")
        print(f"        맡을 역할: {person.get('fitsRole', '')}")
        print(f"        추천 이유: {person.get('reason', '')}")
        print()
    print("=" * 60)


def recommend_questions(vision: dict) -> dict:
    """아이디어 제공자에게 보여줄 '합류 질문 후보'를 AI 가 추천합니다."""
    brief = {
        "serviceName": vision.get("serviceName"),
        "oneLineDesc": vision.get("oneLineDesc"),
        "neededTeammates": [t["role"] for t in vision.get("neededTeammates", [])],
        "matchFactors": vision.get("matchFactors", []),
    }
    user_prompt = (
        "[사업 기획안]\n"
        f"{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        "이 프로젝트에 합류 지원자를 가릴 질문 후보를 JSON 형식으로 추천하세요."
    )
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1000,
        output_config={"effort": "low"},
        system=QUESTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = "".join(b.text for b in response.content if b.type == "text")
    return _extract_json(raw)


# ── experts 스키마 기반 결정적(deterministic) 매칭 점수 — 테이블정의서 v0.2 ──
#    가중치: 기술 40 · 관심 분야 30 · 참여 목적 20 · 협업 시간 10  (+ 하드필터)
_WEEKLY_RANK = {
    "lte_2h": 1, "5h": 2, "10h": 3, "gte_20h": 4,
    "주 2시간 이하": 1, "주 5시간": 2, "주 10시간": 3, "주 20시간 이상": 4,
}
# 온라인 협업이 가능한 전문가 collab_mode (오프라인 필요 프로젝트의 하드필터 판단용)
_ONLINE_ONLY_COLLAB = {"online_only", "온라인만"}


def _cap_rank(v) -> int:
    """주당 투입 값을 비교용 랭크로. 목록값은 매핑, '주 N시간' 같은 직접 입력은 숫자로 환산."""
    if v in _WEEKLY_RANK:
        return _WEEKLY_RANK[v]
    digits = "".join(ch for ch in str(v or "") if ch.isdigit())
    if not digits:
        return 0
    h = int(digits)
    return 1 if h <= 2 else 2 if h <= 5 else 3 if h <= 10 else 4


def _as_tokens(value) -> list:
    """문자열('a, b')/리스트를 토큰 리스트로 정규화."""
    if value is None:
        return []
    items = value if isinstance(value, list) else str(value).replace("/", ",").split(",")
    return [str(t).strip() for t in items if t and str(t).strip()]


def _norm(s) -> str:
    return str(s).replace(" ", "").lower()


def _overlap(need: list, have: list) -> list:
    """느슨한 토큰 교집합 — 양방향 부분일치 허용(한국어 표현 차이 흡수)."""
    matched = []
    for x in need:
        nx = _norm(x)
        if nx and any(nx in _norm(y) or _norm(y) in nx for y in have):
            matched.append(x)
    return matched


def _nat(tokens: list) -> list:
    """참여 목적/프로젝트 성격 어휘 정규화: '창업 기회' → '창업'."""
    return ["창업" if _norm(t) == _norm("창업 기회") else t for t in tokens]


def compute_match_score(expert: dict, project: dict) -> dict:
    """전문가 프로필 ↔ 프로젝트 matchProfile 을 비교해 0~100 점수와 항목별 근거를 만든다."""
    mp = project or {}
    p_skills = _as_tokens(mp.get("roleSkills"))
    p_domains = _as_tokens(mp.get("domains"))
    p_natures = _nat(_as_tokens(mp.get("natures")))
    p_min_cap = mp.get("minWeeklyCapacity")
    p_meeting = mp.get("meetingMode") or "online_only"

    e_skills = _as_tokens(expert.get("primaryRole")) + _as_tokens(expert.get("skills"))
    e_domains = _as_tokens(expert.get("interestDomains"))
    e_natures = _nat(_as_tokens(expert.get("participationMotivation")))
    e_cap = expert.get("weeklyCapacity")
    e_contact = _as_tokens(expert.get("contactHours"))
    e_collab = expert.get("collabMode")

    # ── 하드필터: 주당 투입 ≥ 최소요건, 오프라인 필요 시 온라인-온리 탈락
    cap_ok = (not p_min_cap) or (_cap_rank(e_cap) >= _cap_rank(p_min_cap))
    hard_reasons = []
    if not cap_ok:
        hard_reasons.append(f"주당 투입이 프로젝트 최소({p_min_cap})에 미달")
    if p_meeting == "offline_optional" and e_collab and _norm(e_collab) in {_norm(x) for x in _ONLINE_ONLY_COLLAB}:
        hard_reasons.append("오프라인 협업이 필요한데 온라인만 가능")
    hard_pass = not hard_reasons

    def _ratio(matched, total):
        return (len(matched) / total) if total else 1.0  # 프로젝트가 요구하지 않으면 만점

    m_skill = _overlap(p_skills, e_skills)
    m_dom = _overlap(p_domains, e_domains)
    m_nat = _overlap(p_natures, e_natures)
    time_ratio = (0.7 if cap_ok else 0.0) + (0.3 if e_contact else 0.0)

    comps = [
        {"key": "기술 적합도", "weight": 40, "ratio": _ratio(m_skill, len(p_skills)),
         "detail": f"필요 역량 {len(m_skill)}/{len(p_skills) or 0} 일치"
                   + (f" ({', '.join(m_skill)})" if m_skill else "")},
        {"key": "관심 분야", "weight": 30, "ratio": _ratio(m_dom, len(p_domains)),
         "detail": f"겹친 분야: {', '.join(m_dom) or '없음'}"},
        {"key": "참여 목적", "weight": 20, "ratio": _ratio(m_nat, len(p_natures)),
         "detail": f"겹친 목적: {', '.join(m_nat) or '없음'}"},
        {"key": "협업 시간", "weight": 10, "ratio": min(1.0, time_ratio),
         "detail": ("주당 투입 충분" if cap_ok else "주당 투입 부족")
                   + (" · 연락 시간 명시" if e_contact else "")},
    ]
    for c in comps:
        c["got"] = round(c["weight"] * c["ratio"], 1)
    score = round(sum(c["got"] for c in comps))
    if not hard_pass:
        score = min(score, 45)  # 하드필터 탈락 시 상한

    return {
        "score": int(score),
        "hardPass": hard_pass,
        "hardReasons": hard_reasons,
        "components": [
            {"key": c["key"], "weight": c["weight"], "got": c["got"],
             "pct": round(c["ratio"] * 100), "detail": c["detail"]}
            for c in comps
        ],
    }


def preview_scores(applicant: dict, projects: list) -> dict:
    """여러 프로젝트의 matchProfile 에 대해 한 지원자의 예상 적합도를 한 번에(즉시) 계산.
    AI 호출 없이 결정적 점수만 내므로 둘러보기 목록 배지에 적합합니다."""
    scores = []
    for mp in projects:
        if mp:
            bd = compute_match_score(applicant, mp)
            scores.append({"score": bd["score"], "hardPass": bd["hardPass"]})
        else:
            scores.append(None)
    return {"scores": scores}


def _verdict_for(breakdown: dict) -> str:
    if not breakdown["hardPass"]:
        return "보류"
    s = breakdown["score"]
    return "강력 추천" if s >= 75 else "추천" if s >= 55 else "보류"


def evaluate_applicant(vision: dict, question_texts: list, applicant: dict,
                       user_answers: list = None) -> dict:
    """지원자 프로필과 필수 질문 3개로, 프로젝트와의 매칭률(%)을 평가합니다.

    지원자가 experts 스키마 프로필을 갖추고(기획안에 matchProfile 이 있으면),
    가중치(기술40·관심30·목적20·시간10)+하드필터로 matchRate 를 '결정적으로' 계산하고,
    AI 는 그 점수/근거에 맞춰 답변·궁합·요약만 생성합니다.

    user_answers 가 주어지면(지원자가 직접 답한 경우) 그 답변을 추정 대신 그대로 평가하고,
    answers.answer 필드는 실제 입력을 진실원천으로 확정합니다.
    """
    match_profile = vision.get("matchProfile")
    is_expert = any(applicant.get(k) for k in
                    ("primaryRole", "interestDomains", "participationMotivation", "weeklyCapacity"))
    breakdown = compute_match_score(applicant, match_profile) if (match_profile and is_expert) else None

    brief = {
        "serviceName": vision.get("serviceName"),
        "oneLineDesc": vision.get("oneLineDesc"),
        "neededTeammates": [t["role"] for t in vision.get("neededTeammates", [])],
        "matchFactors": vision.get("matchFactors", []),
    }
    score_hint = ""
    if breakdown:
        score_hint = (
            "\n[결정적 매칭 점수 — 이 수치를 반드시 그대로 따르세요]\n"
            f"{json.dumps(breakdown, ensure_ascii=False, indent=2)}\n"
            "matchRate 는 위 score 값을 그대로 쓰고, summary·fitItems·answers 를 이 점수와 항목별 근거에 "
            "모순 없게 작성하세요. (하드필터 탈락 시 약점을 솔직히 짚으세요.)\n"
        )
    answers_hint = ""
    if user_answers:
        qa = [{"question": q, "answer": a}
              for q, a in zip(question_texts, user_answers)]
        answers_hint = (
            "\n[지원자가 각 질문에 직접 작성한 답변 — 추정하지 말고 이 답변을 그대로 평가하세요]\n"
            f"{json.dumps(qa, ensure_ascii=False, indent=2)}\n"
            "answers 의 answer 는 위 지원자 답변을 그대로 옮기고(창작·수정 금지), "
            "comment 는 그 답변이 이 자리에 적합한지 한 줄로 평가하세요. "
            "matchRate·fitItems·summary 도 실제 답변 내용을 반영해 판단하세요.\n"
        )
    user_prompt = (
        "[사업 기획안]\n"
        f"{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        "[합류 필수 질문 3개]\n"
        f"{json.dumps(question_texts, ensure_ascii=False, indent=2)}\n\n"
        "[합류 지원자 프로필]\n"
        f"{json.dumps(applicant, ensure_ascii=False, indent=2)}\n"
        f"{score_hint}"
        f"{answers_hint}\n"
        "이 지원자의 매칭률을 JSON 형식으로 평가하세요."
    )
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1200,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": JOIN_SCHEMA}},
        system=JOIN_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = "".join(b.text for b in response.content if b.type == "text")
    result = _extract_json(raw)

    # 결정적 점수가 있으면 그것을 진실원천(source of truth)으로 확정
    if breakdown:
        result["matchRate"] = breakdown["score"]
        result["verdict"] = _verdict_for(breakdown)
        result["breakdown"] = breakdown

    # 지원자가 직접 답한 경우, answer 필드는 실제 입력을 진실원천으로 확정(AI 코멘트만 활용)
    if user_answers:
        ai_answers = result.get("answers", [])
        result["answers"] = [
            {
                "question": question_texts[i] if i < len(question_texts)
                            else ai_answers[i].get("question", "") if i < len(ai_answers) else "",
                "answer": ans,
                "comment": ai_answers[i].get("comment", "") if i < len(ai_answers) else "",
            }
            for i, ans in enumerate(user_answers)
        ]
    return result


def print_join_questions(questions: list) -> None:
    """확정된 합류 필수 질문 3개를 출력합니다."""
    print("\n📋 합류 지원자가 답해야 할 필수 질문 3개 (제공자가 기획서에서 설정)")
    print("=" * 60)
    for i, q in enumerate(questions, 1):
        print(f"   {i}. [{q['by']}] {q['text']}")
    print("=" * 60)


def print_join_result(applicant_name: str, service_name: str, result: dict) -> None:
    """지원자의 답변과 매칭률을 출력합니다."""
    rate = int(result.get("matchRate", 0))
    filled = max(0, min(10, rate // 10))
    bar = "█" * filled + "░" * (10 - filled)
    print(f"\n🙋 {applicant_name} 님이 '{service_name}'에 합류 신청했어요")
    print("=" * 60)
    for i, a in enumerate(result.get("answers", []), 1):
        print(f"   Q{i}. {a.get('question', '')}")
        print(f"       💬 {a.get('answer', '')}")
        print(f"       ↳ {a.get('comment', '')}")
        print()
    print(f"   🎯 매칭률: {rate}%   [{bar}]")
    print(f"   📌 평가: {result.get('verdict', '')} — {result.get('summary', '')}")
    print("=" * 60)


def print_slack_invite(service_name: str, applicant_name: str) -> None:
    """양측이 수락하면 슬랙 채팅방으로 안내합니다."""
    print("\n🎉 서로 수락했어요! 이제 이 여정을 함께 시작합니다.")
    print("=" * 60)
    print(f"   '{service_name}' 프로젝트 슬랙 채널에 초대되었습니다.")
    print(f"   👥 참여자: 아이디어 제공자  +  {applicant_name}")
    # 서비스 이름에서 영문·숫자만 뽑아 깔끔한 채널 주소(slug)를 만듭니다.
    slug = "".join(ch for ch in service_name if ch.isascii() and ch.isalnum()).lower() or "project"
    print(f"   🔗 https://orbit-team.slack.com/{slug}  (데모용 링크)")
    print("=" * 60)


def print_vision(idea: str, vision: dict) -> None:
    """만들어진 기획안(또는 되묻기 질문)을 보기 좋게 출력합니다."""
    print(f"\n💡 입력한 아이디어: {idea}\n")

    # (A) 입력이 빈약해서 AI 가 되물어 온 경우
    if vision.get("needMoreInfo"):
        print("🤔 아이디어가 조금 짧아서, 좋은 팀원을 찾으려면 아래가 더 필요해요:")
        for question in vision.get("askFor", []):
            print(f"   • {question}")
        return

    # (B) 정상적으로 기획안이 만들어진 경우
    print("=" * 60)
    print(f"🚀 서비스 이름:  {vision['serviceName']}")
    print(f"🏷  슬로건:      {vision['tagline']}")
    print(f"📝 한 줄 소개:   {vision['oneLineDesc']}\n")

    print("🧩 핵심 기능")
    for feature in vision["features"]:
        print(f"   {feature['icon']} {feature['title']} — {feature['desc']}")
    print()

    plan = vision["plan"]
    print("📊 사업 개요")
    print(f"   • 문제:   {plan['problem']}")
    print(f"   • 해결:   {plan['solution']}")
    print(f"   • 타겟:   {plan['target']}")
    print(f"   • 수익:   {plan['revenue']}\n")

    # ⭐ ORBIT 의 핵심 — 필요한 팀원 (역할 + 합류 매력 한 줄)
    print("👥 필요한 팀원 (neededTeammates) ★ORBIT의 핵심")
    for teammate in vision["neededTeammates"]:
        print(f"   • {teammate['role']}")
        print(f"     └ 💬 {teammate['why']}")
    print()

    # ⭐ ORBIT 의 핵심 — 매칭 중요 요소
    print("🤝 매칭 중요 요소 (matchFactors) ★ORBIT의 핵심")
    for factor in vision["matchFactors"]:
        print(f"   • {factor}")
    print("=" * 60)


if __name__ == "__main__":
    # 명령줄에서 아이디어를 받습니다. 없으면 예시 아이디어를 사용합니다.
    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
    else:
        idea = "페트병 뚜껑을 그립톡으로 재활용하는 사업"
        print("ℹ️  아이디어를 입력하지 않아 예시 아이디어로 실행합니다.")
        print('   (직접 넣으려면:  python src/main.py "나의 아이디어")')

    # ── 발표 데모 설정 (발표자가 이 값만 바꾸면 시나리오를 조정할 수 있어요) ──
    DEMO_PICKED_AI_QUESTIONS = [0, 1]   # 제공자가 고른 AI 추천 질문 번호 (0부터)
    DEMO_FOUNDER_QUESTION = ""          # 제공자가 직접 정한 질문 (비우면 추천 질문 사용)
    DEMO_JOIN_THRESHOLD = 70            # 이 % 이상이면 합류 성사 → 슬랙 안내

    # ── [1/4] 한 줄 아이디어 → 기획서 ──
    print("\n⏳ [1/4] 한 줄 아이디어로 기획서를 만드는 중...")
    vision = generate_vision(idea)
    print_vision(idea, vision)
    if vision.get("needMoreInfo"):
        sys.exit(0)  # 아이디어가 빈약하면 되묻기만 하고 종료

    # ── [2/4] 합류 질문 3개 설정 (아이디어 제공자가 기획서 만들 때) ──
    print("\n⏳ [2/4] 합류 지원자에게 물을 질문을 준비하는 중...")
    qcand = recommend_questions(vision)
    ai_cands = qcand.get("aiQuestionCandidates", [])
    founder_sugs = qcand.get("founderQuestionSuggestions", [])

    print("\n🤖 AI 추천 질문 후보 (이 중에서 제공자가 2개 선택)")
    for i, q in enumerate(ai_cands):
        mark = "✅" if i in DEMO_PICKED_AI_QUESTIONS else "  "
        print(f"   {mark} {q}")
    founder_q = DEMO_FOUNDER_QUESTION or (founder_sugs[0] if founder_sugs else "왜 이 프로젝트에 합류하고 싶나요?")
    print(f"\n👤 제공자가 직접 정한 질문: {founder_q}")

    questions = [{"by": "AI", "text": ai_cands[i]} for i in DEMO_PICKED_AI_QUESTIONS if i < len(ai_cands)]
    questions.append({"by": "제공자", "text": founder_q})
    print_join_questions(questions)

    # ── [3/4] 등록된 팀원 매칭 ──
    print("\n⏳ [3/4] 등록된 팀원 중에서 잘 맞는 사람을 찾는 중...")
    matches = match_teammates(vision)
    print_matches(matches)

    found = matches.get("matches", [])
    if not found:
        sys.exit(0)

    # ── [4/4] 합류 신청 → 3개 질문 답변 → 매칭률 ──
    applicant_name = found[0]["name"]  # 매칭 1위가 합류 신청한다고 가정
    applicant = next((p for p in TEAMMATE_POOL if p["name"] == applicant_name), {"name": applicant_name})
    print(f"\n⏳ [4/4] {applicant_name} 님의 합류 적합도(매칭률)를 평가하는 중...")
    result = evaluate_applicant(vision, [q["text"] for q in questions], applicant)
    print_join_result(applicant_name, vision["serviceName"], result)

    # ── 양측 수락 → 슬랙 채팅방 안내 ──
    if int(result.get("matchRate", 0)) >= DEMO_JOIN_THRESHOLD:
        print_slack_invite(vision["serviceName"], applicant_name)
    else:
        print(f"\n📭 매칭률이 {DEMO_JOIN_THRESHOLD}% 미만이라 아직 합류 안내를 보내지 않았어요.")
