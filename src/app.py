"""
ORBIT 웹 서버
- 브라우저(앞쪽)는 화면만 그리고, 실제 Claude API 호출은 이 서버(뒤쪽)가 합니다.
  → 그래서 API 키가 브라우저에 노출되지 않아 안전합니다.
- 이미 만든 main.py 의 함수들을 그대로 재사용합니다.

실행:
    python src/app.py
그다음 브라우저에서  http://localhost:5001  로 접속하세요.
"""

import os
import sys

# 같은 폴더의 main.py 를 불러올 수 있게 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, render_template, request

import main  # generate_vision, recommend_questions, match_teammates, evaluate_applicant, TEAMMATE_POOL

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/boost")
def api_boost():
    """[보충] 한 줄 아이디어 → 객관식 보충 질문 2개."""
    idea = (request.json or {}).get("idea", "").strip()
    if not idea:
        return jsonify({"error": "아이디어를 입력해 주세요."}), 400
    return jsonify(main.generate_boost_questions(idea))


@app.post("/api/vision")
def api_vision():
    """[1단계] 한 줄 아이디어(+보충답변) → 비전 페이지."""
    data = request.json or {}
    idea = data.get("idea", "").strip()
    if not idea:
        return jsonify({"error": "아이디어를 입력해 주세요."}), 400
    return jsonify(
        main.generate_vision(
            idea,
            target_answer=data.get("targetAnswer", ""),
            strength_answer=data.get("strengthAnswer", ""),
        )
    )


@app.post("/api/questions")
def api_questions():
    """[2단계] 합류 질문 후보 추천."""
    vision = (request.json or {}).get("vision", {})
    return jsonify(main.recommend_questions(vision))


@app.post("/api/match")
def api_match():
    """[3단계] 등록된 팀원 중 매칭. variety(다시 찾기 횟수)로 하위 후보를 회전 노출."""
    data = request.json or {}
    vision = data.get("vision", {})
    try:
        variety = int(data.get("variety", 0) or 0)
    except (TypeError, ValueError):
        variety = 0
    return jsonify(main.match_teammates(vision, variety))


@app.post("/api/preview")
def api_preview():
    """[둘러보기] 프로필 보유 Rider에게 카드별 예상 적합도를 즉시(AI 없이) 계산."""
    data = request.json or {}
    applicant = data.get("applicant") or {}
    projects = data.get("projects") or []
    return jsonify(main.preview_scores(applicant, projects))


@app.post("/api/evaluate")
def api_evaluate():
    """[4단계] 합류 지원자의 매칭률 평가."""
    data = request.json or {}
    vision = data.get("vision", {})
    question_texts = data.get("questions", [])
    user_answers = data.get("answers")  # 지원자가 직접 입력한 답변(있으면 추정 대신 그대로 평가)
    # 이력서(프로필 객체)를 직접 받으면 그대로 사용, 없으면 이름으로 데모 팀원 풀에서 조회
    applicant = data.get("applicant")
    if not applicant:
        applicant_name = data.get("applicantName", "")
        applicant = next(
            (p for p in main.TEAMMATE_POOL if p["name"] == applicant_name),
            {"name": applicant_name},
        )
    return jsonify(main.evaluate_applicant(vision, question_texts, applicant, user_answers))


@app.post("/api/riders")
def api_riders():
    """[둘러보기] 등록된 라이더(팀원+투자자) 목록."""
    return jsonify(main.list_riders())


@app.post("/api/investeval")
def api_investeval():
    """[투자] 투자자 Q&A 검토 — 답변 코멘트·제공자 답변·관심도."""
    data = request.json or {}
    return jsonify(main.evaluate_investor(
        data.get("vision", {}), data.get("investor", {}),
        data.get("questions", []), data.get("answers", []),
        data.get("investorQuestion", ""),
    ))


@app.post("/api/bizreview")
def api_bizreview():
    """[투자] AI 사업성 검토 — 아이디어 단계 정성 분석(투자 관점)."""
    data = request.json or {}
    return jsonify(main.review_business(data.get("vision", {}), data.get("investor", {})))


if __name__ == "__main__":
    # 5001 포트로 실행 (5000은 macOS 가 쓰는 경우가 있어 피했습니다)
    app.run(host="127.0.0.1", port=5001, debug=True)
