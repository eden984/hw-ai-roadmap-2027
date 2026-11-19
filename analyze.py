"""H/W 개발 업무 48개 평가 데이터셋 → EDA → 웨이브 분류 → 결과(json, csv, svg)."""
import csv, json, math, pathlib, statistics as st
from decimal import Decimal, ROUND_HALF_UP
def rnd(x, n=1): return float(Decimal(str(x)).quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP))

OUT = pathlib.Path(__file__).parent
# (단계, 업무, 주당시간, AI역량2025, AI역량2027, 오류비용, 검증용이성, 데이터준비도)  점수는 1~5
RAW = """기획|경쟁 제품·시장 조사|1.0|3|4.5|1|3|4
기획|요구사항 문서(PRD) 작성|1.0|3|4|3|3|3
기획|사양 비교표 작성|0.5|3.5|4.5|2|4|4
기획|원가 목표 시뮬레이션|0.5|2|3.5|3|3|2
기획|안전·EMC 인증 요건 조사(KC·CE·FCC)|0.5|2.5|4|4|3|3
기획|개발 일정 계획|0.5|2|3|3|2|2
회로|부품 선정·대체품 탐색|1.5|2.5|4|3|4|3
회로|데이터시트 요약·핀맵 정리|1.0|3.5|4.5|3|4|5
회로|회로도 리뷰|1.5|1.5|3|5|3|2
회로|전원·소비전류 계산|1.0|2.5|4|4|5|3
회로|회로 시뮬레이션(SPICE)|1.0|1.5|3|3|4|2
회로|ESD·안전 보호 설계|1.0|1.5|2.5|5|2|2
PCB·기구|부품 배치(Placement)|1.0|1.5|3|4|3|2
PCB·기구|배선(Routing)|1.5|1.5|3|4|3|2
PCB·기구|DRC·DFM 검토|0.5|3|4|3|5|3
PCB·기구|열 해석|0.5|2|3|4|3|2
PCB·기구|안테나·RF 튜닝|1.0|1|2|4|2|1
PCB·기구|기구 간섭 검토|0.5|2|3|3|4|2
펌웨어|드라이버·HAL 코드 작성|2.0|3.5|4.5|3|4|4
펌웨어|단위 테스트 작성|1.0|3.5|4|2|5|4
펌웨어|코드 리뷰|1.0|3|4|3|4|4
펌웨어|저전력 최적화|1.5|2|3.5|4|4|3
펌웨어|부트로더·OTA|1.0|2|3|5|3|3
펌웨어|디버깅·로그 분석|1.5|3|4.5|2|4|4
BOM·구매|BOM 정합성 검사|0.5|3|4.5|3|5|4
BOM·구매|단종(EOL) 모니터링|0.5|2.5|4.5|3|4|3
BOM·구매|견적·단가 비교|0.5|3|4.5|2|4|3
BOM·구매|대체 부품 승인|1.0|1.5|3|5|3|2
BOM·구매|리드타임·재고 관리|0.5|2.5|4|3|4|2
BOM·구매|협력사 커뮤니케이션|1.0|3|4|2|3|3
시험·검증|시험 계획서 작성|0.5|3|4.5|3|4|3
시험·검증|자동 시험 스크립트|1.0|3|4.5|2|5|3
시험·검증|측정 데이터 분석|1.5|3|4.5|4|4|3
시험·검증|불량 원인 분석(FA)|1.0|1.5|3|4|2|2
시험·검증|EMC 사전 시험 대응|1.0|1|2|5|2|1
시험·검증|신뢰성(환경) 시험|1.0|1.5|2.5|4|3|2
양산·품질|양산 이관 문서|0.5|3|4.5|3|3|3
양산·품질|공정 불량 데이터 분석|0.5|2.5|4|3|4|2
양산·품질|검사 지그 펌웨어|0.5|3|4|4|5|3
양산·품질|변경점 관리(ECN)|0.5|2.5|4|4|4|3
양산·품질|필드 불량 분석|1.5|2|3.5|4|3|2
양산·품질|수율 개선|0.5|1.5|3|3|3|2
문서·협업|회의록 정리|0.5|4.5|5|1|4|5
문서·협업|기술 문서·매뉴얼|1.0|3.5|4.5|2|4|4
문서·협업|사내 보고서|0.5|4|5|2|4|4
문서·협업|해외 협력사 이메일·번역|0.5|4.5|5|2|4|5
문서·협업|특허·선행기술 조사|0.5|2.5|4|2|3|3
문서·협업|신입 교육 자료|0.5|3.5|4.5|1|4|4
시험·검증|온도 센서 교정·정확도 검증(KOLAS)|1.0|2|3|5|4|3
기획|통신사 망연동·전파 인증 대응(국내 3사·KC 전파·PTCRB)|0.5|2.5|4|4|3|3
BOM·구매|배터리 운송 규정 대응(UN38.3)|0.5|2.5|4|4|3|3
시험·검증|저온(-20~-80°C) 배터리 특성 시험|1.0|1.5|2.5|4|3|2
펌웨어|데이터 무결성 로깅(GDP·Part 11)|1.0|2|3.5|5|3|2
PCB·기구|방수(IP67) 구조 검토|0.5|1.5|2.5|4|3|2
펌웨어|서버 통신 프로토콜·페이로드 설계(MQTT·LTE-M)|1.0|2.5|4|4|4|3"""
STAGES = ["기획", "회로", "PCB·기구", "펌웨어", "BOM·구매", "시험·검증", "양산·품질", "문서·협업"]
WAVES = {
    "W1": {"name": "바로 맡긴다", "en": "Delegate", "q": "2027 Q1", "color": "#2251FF"},
    "W2": {"name": "AI 초안 + 사람 검증", "en": "Co-pilot", "q": "2027 Q2", "color": "#00A9F4"},
    "W3": {"name": "데이터부터 쌓는다", "en": "Build data", "q": "2027 Q3", "color": "#8A9BA8"},
    "W4": {"name": "사람이 지킨다", "en": "Guard", "q": "2027 Q4", "color": "#051C2C"},
}

def wave(r):
    if r["err"] >= 5: return "W4"  # 오류 비용 최고 등급은 무조건 사람이 지킨다
    hi = r["cap27"] >= 3.5
    if hi and r["err"] <= 2: return "W1"
    if hi: return "W2"
    if r["err"] <= 3: return "W3"
    return "W4"

def save_rate(r):  # 2027년 AI로 줄일 수 있는 시간 비율(가정식)
    return 0.75 * ((r["cap27"] - 1) / 4) * (1 - 0.15 * (r["err"] - 1)) * (0.6 + 0.08 * r["verif"])

rows = []
for line in RAW.splitlines():
    s, t, h, c25, c27, e, v, d = line.split("|")
    r = dict(stage=s, task=t, hours=float(h), cap25=float(c25), cap27=float(c27), err=int(e), verif=int(v), data=int(d))
    r["uplift"] = r["cap27"] - r["cap25"]
    r["rate"] = round(save_rate(r), 3)
    r["saved"] = round(r["hours"] * r["rate"], 3)
    r["wave"] = wave(r)
    rows.append(r)

with open(OUT / "data.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def pearson(a, b):
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return num / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))

VARS = [("hours", "주당 시간"), ("cap25", "AI 역량 2025"), ("cap27", "AI 역량 2027"), ("uplift", "역량 상승폭"),
        ("err", "오류 비용"), ("verif", "검증 용이성"), ("data", "데이터 준비도")]
corr = [[round(pearson([r[a] for r in rows], [r[b] for r in rows]), 2) for b, _ in VARS] for a, _ in VARS]

total_h = sum(r["hours"] for r in rows)
total_saved = sum(r["saved"] for r in rows)
by_stage = []
for s in STAGES:
    g = [r for r in rows if r["stage"] == s]
    by_stage.append(dict(stage=s, hours=sum(r["hours"] for r in g), cap25=round(st.mean(r["cap25"] for r in g), 2),
                         cap27=round(st.mean(r["cap27"] for r in g), 2), saved=round(sum(r["saved"] for r in g), 2),
                         err=round(st.mean(r["err"] for r in g), 2)))
by_wave = {}
for k in WAVES:
    g = [r for r in rows if r["wave"] == k]
    by_wave[k] = dict(n=len(g), hours=round(sum(r["hours"] for r in g), 1), saved=round(sum(r["saved"] for r in g), 1),
                      tasks=[r["task"] for r in sorted(g, key=lambda r: -r["saved"])])
ranked = sorted(rows, key=lambda r: -r["saved"])
cum, top10 = 0, 0
for i, r in enumerate(ranked):
    cum += r["saved"]
    if i == 9: top10 = cum
uplift_hist = {}
for r in rows: uplift_hist[r["uplift"]] = uplift_hist.get(r["uplift"], 0) + 1

S = dict(
    n=len(rows), total_h=round(total_h, 1), total_saved=round(total_saved, 1), saved_pct=round(100 * total_saved / total_h),
    top10_pct=round(100 * top10 / total_saved), top10_n=10,
    mean_cap25=rnd(st.mean(r["cap25"] for r in rows), 1), mean_cap27=rnd(st.mean(r["cap27"] for r in rows), 1),
    mean_uplift=round(st.mean(r["uplift"] for r in rows), 2),
    r_cap27_err=corr[2][4], r_cap27_data=corr[2][6], r_cap27_verif=corr[2][5], r_uplift_cap25=corr[3][1],
    by_stage=by_stage, by_wave=by_wave, waves=WAVES, corr=corr, vars=[v for _, v in VARS],
    uplift_hist=sorted(uplift_hist.items()), top=[(r["task"], r["stage"], round(r["saved"], 2), r["wave"]) for r in ranked[:10]],
)
low_data = [r for r in rows if r["data"] <= 2]
S["low_data_n"] = len(low_data)
S["low_data_cap27"] = round(st.mean(r["cap27"] for r in low_data), 2)
S["hi_data_cap27"] = round(st.mean(r["cap27"] for r in rows if r["data"] >= 4), 2)
json.dump(dict(stats=S, rows=rows), open(OUT / "stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in S.items() if k not in ("by_stage", "corr", "rows", "waves")}, ensure_ascii=False, indent=1))
for b in by_stage: print(b)

# ── 차별화: 백색가전 H/W 일반 프로파일 vs IoT 물류 로거(윌로그형) 2027 목표 프로파일 (1~5, 가정 점수)
DIFF = [("필드 데이터 루프 속도", 3.5, 5, "로거는 데이터 자체가 고객에게 파는 상품"),
        ("출시 반복 속도", 2.5, 4, "소량 다품종이라 AI 프로토타이핑 효과가 크다"),
        ("저전력·무선 최적화 깊이", 2.5, 5, "LTE-M·BLE·배터리 수명이 제품 경쟁력"),
        ("디바이스-클라우드 통합", 3.5, 4.5, "기기·서버·고객 리포트를 한 사람이 꿰뚫는다"),
        ("고객 규제 대응(GDP·콜드체인)", 2, 4.5, "의약품·식품 유통 규정 문서를 AI로 빠르게"),
        ("소량 다품종 대응", 2, 4, "고객별 커스텀 펌웨어·설정"),
        ("기구·안전 규격 깊이(IEC 60335)", 5, 3, "가전의 강점. 정면 승부하지 않는다"),
        ("양산 규모의 경제", 5, 2, "가전의 강점. 정면 승부하지 않는다")]
d = json.load(open(OUT / "stats.json", encoding="utf-8"))
d["stats"]["diff"] = [dict(dim=a, appl=b, iot=c, note=n, gap=round(c - b, 1)) for a, b, c, n in DIFF]
json.dump(d, open(OUT / "stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("diff added", len(DIFF))
