import json
import pathlib

P = json.load(open(pathlib.Path(__file__).parent / "packets.json"))
orders = {
    "j1": ["A1", "B1", "A2", "B2"],
    "j2": ["B2", "A2", "B1", "A1"],
    "j3": ["A2", "B2", "A1", "B1"],
}
labels = ["가", "나", "다", "라"]
brief = """[브리프]
제품: 슬로우브루 — 12시간 저온 추출 콜드브루 원액 파우치. 1팩으로 4잔. 파우치 1/4을 물이나 우유 150ml에 붓고 얼음을 넣으면 끝, 30초.
타깃: 출근 전 5분이 아까운 30대 직장인. 경쟁: 편의점 RTD 커피, 캡슐 머신.
강점: 산미 낮고 쓴맛 적음, 상온 6개월, 잔당 900원. 캠페인 목적: 출시 인지.
톤: 담백하고 위트 있게. 금지: 과장된 최상급, 명령조, 경쟁 제품 실명·직접 비교, 건강 효능 주장. 브랜드명 필수.
채널: 인스타그램 피드(아침 식탁 위 파우치와 유리잔 한 컷 이미지 + 헤드라인·캡션·CTA), 지하철 스크린도어(메인 20자·서브 30자 이내)."""
for j, order in orders.items():
    parts = [
        brief,
        "\n아래는 서로 다른 카피라이터 네 명이 같은 브리프로 낸 시안 묶음입니다. 각 묶음은 인스타그램 3세트와 스크린도어 3줄입니다.\n",
    ]
    for lab, key in zip(labels, order):
        p = P[key]
        parts.append(f"\n=== 묶음 {lab} ===")
        for i, (h, c, cta) in enumerate(p["ig"], 1):
            parts.append(f"[인스타 {i}] 헤드라인: {h}\n캡션: {c}\nCTA: {cta}")
        for i, (m, s) in enumerate(p["sd"], 1):
            parts.append(f"[스크린도어 {i}] 메인: {m} / 서브: {s}")
    parts.append("""
광고 크리에이티브 디렉터로서 내부 시안 회의에 올릴 묶음을 고르는 상황입니다. 도구를 쓰지 말고 위 텍스트만으로 평가하세요.
1. 묶음마다 다음 여섯 기준을 1~10점으로 매기고 한 줄 근거를 다세요: 주목도(스크롤·통행 중 멈추게 하는 힘), 출시·브랜드 인지, 타깃 인사이트, 톤 준수(담백·위트, 금지 표현 없음), 사실 충실(브리프에 없는 사실을 지어냈는지), 채널 적합(두 매체의 읽는 상황에 맞는지).
2. 네 묶음의 종합 순위.
3. 묶음과 무관하게 가장 좋은 인스타 세트 하나와 가장 좋은 스크린도어 줄 하나를 "묶음 X 인스타 n"처럼 지목하고 이유를 한 줄로.
4. 브리프 위반이나 사실 오류가 있으면 전부 지목.
마지막 줄에 JSON 한 줄로: {"scores": {"가": [6개 점수], ...}, "rank": ["가",...], "best_ig": "가-1", "best_sd": "가-1"}""")
    (pathlib.Path(__file__).parent / f"{j}.txt").write_text("\n".join(parts))
json.dump(
    {j: dict(zip(labels, o)) for j, o in orders.items()},
    open(pathlib.Path(__file__).parent / "key.json", "w"),
)
