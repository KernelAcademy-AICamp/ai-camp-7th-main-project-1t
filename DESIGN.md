---
name: ORBIT Design System
description: 아이디어를 함께할 사람과 연결하는 AI 팀빌딩 플랫폼 ORBIT의 색·타이포·컴포넌트 규칙
theme: light
concept: 네이비 단색 기반 + 쨍한 파랑 포인트. 청록·민트·초록은 쓰지 않음.
colors:
  # 브랜드
  navy: '#0f172a'       # 주색 · 버튼 · 헤더 · 제목 · 텍스트 강조 · 로고
  blue: '#2563eb'       # 포인트(쨍한 파랑) · 로고 슬래시 · 링크 · 핵심 하이라이트
  blue-deep: '#1e4fd6'  # eyebrow · 진행바 · 밝은 배경 위 강조 텍스트
  blue-light: '#3b82f6' # 밝은 파랑 변형 · 보조 강조
  sky: '#eff4ff'        # 정보 배경 · 입력창 · 태그 배경
  # 표면 · 뉴트럴
  bg: '#f8fafc'         # 페이지 배경(오프화이트)
  card: '#ffffff'       # 카드 · 표면
  text: '#191c1e'       # 본문 텍스트
  muted: '#64748b'      # 보조 텍스트 · 설명
  line: '#e2e8f0'       # 테두리 · 구분선
  # 시맨틱(의미 색)
  success: '#2563eb'    # 완료 · 성공 → 파랑으로 통일(초록 미사용)
  success-bg: '#dbeafe' # 완료 배경(옅은 파랑)
  amber: '#d97706'      # 경고 · 승인 대기 · 보통
  amber-ink: '#92400e'  # 경고 텍스트
  amber-bg: '#fffbeb'   # 경고 배경
  error: '#dc2626'      # 오류 · 실패
typography:
  fontFamily: "'Inter', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif"
  note: 영문·숫자는 Inter, 한글은 Noto Sans KR. Google Fonts로 로드.
  baseLineHeight: '1.6'
  wordBreak: 'keep-all'   # 한국어 줄바꿈 자연스럽게
  scale:
    display:  { size: 30px, weight: 900, tracking: '-0.02em' }   # 히어로 · 큰 제목
    h1:       { size: 22px, weight: 800 }                        # 화면 제목
    h2:       { size: 18px, weight: 900 }                        # 섹션 제목
    body:     { size: 14px, weight: 400, color: text }
    small:    { size: 12.5px, weight: 400, color: muted }
    eyebrow:  { size: 12px, weight: 800, tracking: '0.03em', color: blue-deep }  # 카드 상단 라벨
    button:   { size: 14.5px, weight: 800 }
radius:
  button: 10px
  input: 12px
  card: 16px
  pill: 999px
shadow:
  card: '0 10px 30px rgba(15,23,42,.04)'
spacing:
  cardPadding: '22px 24px'
  buttonPadding: '13px 20px'
  sectionGap: '16px'
---

# ORBIT Design System

ORBIT은 **한 줄 아이디어 → AI 기획안 → 딱 맞는 팀원·투자자 매칭**을 잇는 플랫폼입니다.
디자인은 **네이비 단색**을 기본으로 하고, **쨍한 파랑**을 포인트로만 씁니다.
청록·민트·초록 계열은 사용하지 않으며, 상태 색은 파랑(성공)·앰버(경고)·빨강(오류)으로 단순화했습니다.

## 1. 색 (Color)

### 브랜드
| 토큰 | HEX | 쓰임 |
|---|---|---|
| `navy` | `#0F172A` | 주색 — 버튼·헤더·제목·텍스트 강조·로고 |
| `blue` | `#2563EB` | 포인트(쨍한 파랑) — 로고 슬래시·링크·핵심 하이라이트 |
| `blue-deep` | `#1E4FD6` | eyebrow·진행바·밝은 배경 위 강조 텍스트 |
| `blue-light` | `#3B82F6` | 밝은 파랑 변형·보조 강조 |
| `sky` | `#EFF4FF` | 정보 배경·입력창·태그 배경 |

### 표면 · 뉴트럴
| 토큰 | HEX | 쓰임 |
|---|---|---|
| `bg` | `#F8FAFC` | 페이지 배경(오프화이트) |
| `card` | `#FFFFFF` | 카드·표면 |
| `text` | `#191C1E` | 본문 텍스트 |
| `muted` | `#64748B` | 보조 텍스트·설명 |
| `line` | `#E2E8F0` | 테두리·구분선 |

### 시맨틱 (의미 색)
| 상태 | 배경 | 텍스트/강조 | 쓰임 |
|---|---|---|---|
| 성공·완료 | `#DBEAFE` | `#1E4FD6` / `#2563EB` | 합류 완료, 승인 완료 (**초록 대신 파랑으로 통일**) |
| 경고·대기 | `#FFFBEB` | `#92400E` / `#D97706` | 승인 대기중, 보통 |
| 오류 | `#FEF2F2` | `#DC2626` | 실패, 필수 조건 미충족 |

> **원칙** — 기본은 네이비, 포인트는 쨍한 파랑. **청록·민트·초록은 쓰지 않는다.** 상태 표시도 초록을 배제하고 파랑/앰버/빨강으로만.

## 2. 타이포그래피 (Typography)

- **폰트**: `Inter`(영문·숫자) + `Noto Sans KR`(한글) — Google Fonts 로드
- **줄바꿈**: `word-break: keep-all` — 한국어 단어가 어색하게 끊기지 않도록
- **기본 행간**: `1.6`

| 역할 | 크기 | 굵기 | 비고 |
|---|---|---|---|
| Display | 30px | 900 | 히어로·큰 제목, 자간 -0.02em |
| 화면 제목 (h1) | 22px | 800 | |
| 섹션 제목 (h2) | 18px | 900 | navy |
| 본문 | 14px | 400 | text |
| 보조 | 12.5px | 400 | muted |
| Eyebrow 라벨 | 12px | 800 | blue-deep, 자간 0.03em |
| 버튼 | 14.5px | 800 | |

## 3. 컴포넌트 (Components)

### 버튼 `.btn`
- 기본: 배경 `navy`, 흰 글씨, radius `10px`, 패딩 `13px 20px`, 굵기 800
- **호버: 색이 바뀌지 않고 살짝 진해지기만 함** (호버 시 다른 색 라인/테두리 없음)
- `.btn.ghost`: 흰 배경 + `line` 테두리 + navy 글씨 (보조 액션)
- 긍정 액션(합류·수락 등)도 파랑 계열 사용

### 카드 `.card`
- 배경 `card`, 테두리 `1px line`, radius `16px`, 패딩 `22px 24px`
- 그림자 `0 10px 30px rgba(15,23,42,.04)`
- 상단에 `.eyebrow`(이모지 + 12px/800/blue-deep)로 섹션 성격 표시

### 배지/알약 `.pill`
- radius `999px`, 작은 글씨(10~12px)·굵기 800
- 파랑(정보/완료) · 앰버(대기/주의) — 초록 미사용

### 입력 (input / textarea)
- 테두리 `1px line`, radius `12px`
- 포커스 시 파랑 테두리 + 옅은 파랑 글로우 링

### 진행/적합도 바 (progress)
- 트랙 `line`, 채움 `blue-deep`(파랑), radius `999px`

### 아이콘
- 체크 표시는 초록 이모지(✅) 대신 **단색 체크(✓)** — 주변 글자색을 따라감
- 목록/둘러보기 아이콘은 🔍 등 의미에 맞는 아이콘 사용

## 4. 레이아웃 원칙

- **모바일 우선**: 좁은 폭(SPA) 기준. `.narrow` 컨테이너 + `pagepad`
- **간격은 레이아웃으로**: 형제 요소는 `gap`(flex/grid)으로. 카드 간격 `16px`
- **스크롤 밀림 방지**: `html{overflow-y:scroll}` 로 스크롤바 자리 항상 확보
- **표면 위계**: 페이지(`bg`) < 카드(`card`) < 강조 배경(`sky`)
- **히어로 그라데이션**: 네이비 → 파랑 (예: `#0F172A → #1E3A8A`). 청록/초록 스톱 금지

## 5. 보이스 & 톤

- 비전공자도 이해할 쉬운 한국어. 시스템 용어 대신 사용자 언어("합류", "제안", "발급")
- 버튼은 결과를 말한다: "합류 신청 보내기 →", "참여 확인서 발급 →"
- 이모지는 섹션 성격을 빠르게 전달하는 보조 신호로만 (🚀 Shooter · 🛰 Rider)

---

_이 문서는 현재(라이트 테마) ORBIT 앱 `src/templates/index.html` 의 실제 값을 기준으로 정리한 것입니다.
색을 바꾸려면 `:root` 의 토큰만 교체하면 앱 전체에 반영됩니다._
