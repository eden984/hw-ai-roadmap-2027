"""stats.json → 맥킨지 스타일 index.html (차트는 인라인 SVG)."""
import json, math, pathlib, html

OUT = pathlib.Path(__file__).parent
D = json.load(open(OUT / "stats.json", encoding="utf-8"))
S, ROWS = D["stats"], D["rows"]
W = S["waves"]
NAVY, BLUE, CYAN, GREY, LINE, INK2 = "#051C2C", "#2251FF", "#00A9F4", "#8A9BA8", "#D0D7DD", "#4B5B67"
e = html.escape

def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}" xmlns="http://www.w3.org/2000/svg" font-family="Noto Sans KR, Malgun Gothic, sans-serif">{body}</svg>'

def t(x, y, s, size=12, fill=INK2, anchor="start", weight=400):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{e(str(s))}</text>'

# Exhibit 1 — 단계별 시간과 AI 역량 이동(2025→2027)
def ex1():
    b, y0, rh = [], 46, 34
    b.append(t(0, 18, "주당 시간(h)", 11, NAVY, weight=700)); b.append(t(330, 18, "평균 AI 역량 (1~5점)  ○ 2025 → ● 2027", 11, NAVY, weight=700))
    for i, v in enumerate([1, 2, 3, 4, 5]):
        x = 360 + (v - 1) * 85
        b.append(f'<line x1="{x}" y1="30" x2="{x}" y2="{y0 + 8 * rh - 10}" stroke="{LINE}" stroke-dasharray="2 3"/>'); b.append(t(x, y0 + 8 * rh + 4, v, 10, GREY, "middle"))
    for i, s in enumerate(S["by_stage"]):
        y = y0 + i * rh
        b.append(t(0, y + 4, s["stage"], 12, NAVY, weight=500))
        bw = s["hours"] / 8 * 150
        b.append(f'<rect x="90" y="{y - 9}" width="{bw:.1f}" height="16" fill="{NAVY}"/>'); b.append(t(95 + bw, y + 4, f'{s["hours"]:g}', 11, NAVY))
        x1, x2 = 360 + (s["cap25"] - 1) * 85, 360 + (s["cap27"] - 1) * 85
        b.append(f'<line x1="{x1:.1f}" y1="{y}" x2="{x2:.1f}" y2="{y}" stroke="{BLUE}" stroke-width="2"/>')
        b.append(f'<circle cx="{x1:.1f}" cy="{y}" r="5" fill="#fff" stroke="{BLUE}" stroke-width="2"/><circle cx="{x2:.1f}" cy="{y}" r="6" fill="{BLUE}"/>')
        b.append(t(x2 + 10, y + 4, f'{s["cap27"]:.1f}', 11, BLUE, weight=700))
    return svg(720, y0 + 8 * rh + 14, "".join(b), "단계별 주당 시간과 AI 역량 변화")

# Exhibit 2 — 역량 상승폭 분포
def ex2():
    b, H = [], 170
    mx = max(c for _, c in S["uplift_hist"])
    n = len(S["uplift_hist"]); bw = 110
    for i, (u, c) in enumerate(S["uplift_hist"]):
        x = 60 + i * 150; h = c / mx * H
        col = BLUE if c == mx else NAVY
        b.append(f'<rect x="{x}" y="{200 - h:.1f}" width="{bw}" height="{h:.1f}" fill="{col}"/>')
        b.append(t(x + bw / 2, 194 - h, f"{c}개", 13, col, "middle", 700)); b.append(t(x + bw / 2, 220, f"+{u:g}점", 12, NAVY, "middle"))
    b.append(f'<line x1="40" y1="200" x2="680" y2="200" stroke="{NAVY}"/>')
    return svg(720, 232, "".join(b), "AI 역량 상승폭 분포")

# Exhibit 3 — 상관 행렬
def ex3():
    b, c0, cs, n = [], 128, 74, len(S["vars"])
    for j, v in enumerate(S["vars"]):
        b.append(t(c0 + j * cs + cs / 2, 22, v.replace("AI 역량 ", "역량 "), 10, NAVY, "middle", 500))
    for i, v in enumerate(S["vars"]):
        y = 34 + i * 36
        b.append(t(c0 - 8, y + 23, v, 11, NAVY, "end", 500))
        for j in range(n):
            r = S["corr"][i][j]; a = min(abs(r), 1)
            col = BLUE if r >= 0 else "#E5546C"
            b.append(f'<rect x="{c0 + j * cs + 1}" y="{y + 1}" width="{cs - 2}" height="34" fill="{col}" fill-opacity="{a * 0.85 + 0.04:.2f}"/>')
            b.append(t(c0 + j * cs + cs / 2, y + 23, f"{r:+.2f}" if i != j else "1", 11, "#fff" if a > 0.5 else NAVY, "middle", 700 if a >= 0.6 and i != j else 400))
    return svg(720, 34 + n * 36 + 6, "".join(b), "변수 간 상관 행렬")

# Exhibit 4 — 사분면 산점도
def ex4():
    b = []; X = lambda v: 70 + (v - 1.5) / 3.6 * 620; Y = lambda v: 30 + (v - 0.6) / 4.8 * 330
    b.append(f'<rect x="{X(3.5)}" y="{Y(0.6)}" width="{X(5.1) - X(3.5)}" height="{Y(2.5) - Y(0.6)}" fill="{BLUE}" fill-opacity=".06"/>')
    b.append(f'<line x1="{X(3.5)}" y1="30" x2="{X(3.5)}" y2="360" stroke="{NAVY}" stroke-dasharray="4 3"/>')
    b.append(f'<line x1="{X(3.5)}" y1="{Y(2.5)}" x2="{X(5.1)}" y2="{Y(2.5)}" stroke="{NAVY}" stroke-dasharray="4 3"/>')
    b.append(f'<line x1="70" y1="{Y(3.5)}" x2="{X(3.5)}" y2="{Y(3.5)}" stroke="{NAVY}" stroke-dasharray="4 3"/>')
    for k, (x, y, a) in {"W1": (X(5.05), Y(0.8), "end"), "W2": (X(5.05), Y(5.25), "end"), "W3": (75, Y(0.8), "start"), "W4": (75, Y(5.25), "start")}.items():
        b.append(t(x, y + 4, f'{W[k]["q"]} · {W[k]["name"]}', 12, W[k]["color"] if k != "W3" else INK2, a, 700))
    seen = {}
    lab = {"드라이버·HAL 코드 작성", "회의록 정리", "EMC 사전 시험 대응", "안테나·RF 튜닝", "회로도 리뷰"}
    for r in ROWS:
        key = (r["cap27"], r["err"]); k = seen.get(key, 0); seen[key] = k + 1
        ang = k * 2.4; rad = 0 if k == 0 else 7 + 2 * k
        cx, cy = X(r["cap27"]) + rad * math.cos(ang), Y(r["err"]) + rad * math.sin(ang)
        rr = 3 + math.sqrt(r["hours"]) * 4
        b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="{W[r["wave"]]["color"]}" fill-opacity=".78" stroke="#fff" stroke-width="1"><title>{e(r["task"])} ({r["stage"]}) · {r["hours"]}h</title></circle>')
        if r["task"] in lab:
            b.append(t(cx + rr + 3, cy + 4, r["task"], 10, NAVY))
    for v in [2, 3, 4, 5]: b.append(t(X(v), 378, v, 10, GREY, "middle"))
    for v in [1, 2, 3, 4, 5]: b.append(t(60, Y(v) + 4, v, 10, GREY, "end"))
    b.append(t(380, 396, "2027년 AI 역량 →", 11, NAVY, "middle", 700))
    b.append(f'<text x="18" y="200" font-size="11" fill="{NAVY}" font-weight="700" text-anchor="middle" transform="rotate(-90 18 200)">오류 비용 ↓(아래가 위험)</text>')
    return svg(720, 402, "".join(b), "48개 업무 사분면 산점도")

# Exhibit 5 — 파레토
def ex5():
    rk = sorted(ROWS, key=lambda r: -r["saved"])[:15]; tot = S["total_saved"]
    b, mx, cum, pts = [], rk[0]["saved"], 0, []
    for i, r in enumerate(rk):
        x = 40 + i * 44; h = r["saved"] / mx * 170
        b.append(f'<rect x="{x}" y="{210 - h:.1f}" width="34" height="{h:.1f}" fill="{W[r["wave"]]["color"]}"/>')
        cum += r["saved"]; pts.append((x + 17, 210 - cum / tot * 190 * 1.6))
        b.append(f'<text x="{x + 17}" y="222" font-size="10" fill="{NAVY}" text-anchor="end" transform="rotate(-50 {x + 17} 222)">{e(r["task"])}</text>')
    b.append(f'<polyline points="{" ".join(f"{a:.0f},{c:.0f}" for a, c in pts)}" fill="none" stroke="#E5546C" stroke-width="2"/>')
    for a, c in pts[9:10]:
        b.append(f'<circle cx="{a}" cy="{c:.0f}" r="5" fill="#E5546C"/>'); b.append(t(a - 6, c - 10, f'상위 10개 = 절감의 {S["top10_pct"]}%', 12, "#E5546C", "end", 700))
    b.append(f'<line x1="30" y1="210" x2="700" y2="210" stroke="{NAVY}"/>')
    return svg(720, 330, "".join(b), "절감 가능 시간 파레토")

# Exhibit 6 — 로드맵
ROAD = [
    ("W1", "맡길 일을 AI에 넘긴다", ["회의록·보고서·번역을 AI로 표준화", "측정 데이터·로그 분석 스크립트를 AI로 작성", "단위·자동 시험 코드 AI 생성"], "주 4시간 확보 · 문서 초안 100% AI"),
    ("W2", "AI 초안 + 사람 검증 체계", ["회로·BOM·전원 계산에 '검증 체크리스트' 붙이기", "펌웨어 코드는 AI 작성 → 리뷰 → 테스트 통과만 병합", "단종·대체 부품 모니터링 자동화"], "검증 누락 0건 · 리뷰 시간 30%↓"),
    ("W3", "AI가 배울 사내 데이터를 쌓는다", ["시뮬레이션·시험·불량 이력을 한 저장소로", "설계 결정 기록(왜 이 부품인가) 남기기", "AI용 사내 지식 검색 시범 운영"], "데이터 준비도 2→4점 업무 5개"),
    ("W4", "사람 판단 영역을 명문화한다", ["EMC·RF·안전·OTA는 사람 승인 필수로 규정", "AI 사용 범위·책임 가이드 1장", "2028 계획: 확보한 시간을 설계 품질에 재투자"], "사고 0건 · 가이드 전원 숙지"),
]
def ex6():
    b = []
    for i in range(4):
        x = 150 + i * 142
        b.append(f'<rect x="{x}" y="10" width="138" height="26" fill="{NAVY}"/>'); b.append(t(x + 69, 28, f"2027 Q{i + 1}", 12, "#fff", "middle", 700))
    for i, (k, title, _, kpi) in enumerate(ROAD):
        y = 52 + i * 52; x = 150 + i * 142
        b.append(t(0, y + 20, W[k]["en"], 12, W[k]["color"] if k != "W3" else INK2, weight=700)); b.append(t(0, y + 36, W[k]["name"], 10, INK2))
        b.append(f'<rect x="{x}" y="{y + 6}" width="{720 - x - 4}" height="34" fill="{W[k]["color"]}" fill-opacity="{1 if True else .5}"/>')
        b.append(f'<rect x="{x + 138}" y="{y + 6}" width="{720 - x - 142}" height="34" fill="#fff" fill-opacity=".72"/>')
        b.append(f'<polygon points="{x + 138},{y + 6} {x + 150},{y + 23} {x + 138},{y + 40}" fill="{W[k]["color"]}"/>')
        b.append(t(x + 8, y + 28, f"M{i + 1} " + ["맡기기", "초안+검증", "데이터 쌓기", "판단 명문화"][i], 11.5, "#fff", weight=700))
    b.append(t(150, 270, "■ 집중 실행 분기   ▒ 이후 운영·고도화", 10, GREY))
    return svg(720, 278, "".join(b), "2027 분기별 로드맵")

# Exhibit 7 — 백색가전 대비 차별화
def ex7():
    b = []; X = lambda v: 250 + (v - 1) * 110
    b.append(t(0, 16, "○ 백색가전 H/W 일반 프로파일   ● IoT 물류 로거 2027 목표", 11, NAVY, weight=700))
    for v in range(1, 6): b.append(t(X(v), 34, v, 10, GREY, "middle"))
    for i, d in enumerate(S["diff"]):
        y = 56 + i * 32; adv = d["gap"] > 0
        col = BLUE if adv else GREY
        b.append(t(240, y + 4, d["dim"], 11.5, NAVY, "end", 500))
        b.append(f'<line x1="{X(1)}" y1="{y}" x2="{X(5)}" y2="{y}" stroke="{LINE}"/>')
        b.append(f'<line x1="{X(d["appl"])}" y1="{y}" x2="{X(d["iot"])}" y2="{y}" stroke="{col}" stroke-width="3"/>')
        b.append(f'<circle cx="{X(d["appl"])}" cy="{y}" r="6" fill="#fff" stroke="{NAVY}" stroke-width="2"/><circle cx="{X(d["iot"])}" cy="{y}" r="7" fill="{col}"/>')
        b.append(t(X(max(d["appl"], d["iot"])) + 14, y + 4, f'{d["gap"]:+g}', 11, col, weight=700))
    return svg(720, 56 + 8 * 32, "".join(b), "백색가전 대비 차별화 프로파일")

STRAT = [
    ("01", "필드 데이터 루프 엔지니어", "가전은 출시 뒤 데이터가 늦고 적다. 로거는 기기가 매일 온도·전력·통신 로그를 만든다. AI로 필드 로그를 분석해 펌웨어 개선 주기를 분기 단위에서 월 단위로 줄인다.", "W1·W2"),
    ("02", "전력 예산의 주인", "가전은 콘센트에 꽂힌다. 로거는 배터리 하나로 몇 달을 버틴다. AI로 소비전류 프로파일을 자동 분석하고 배터리 수명을 예측하는 능력을 개인 무기로 만든다.", "W2"),
    ("03", "규제 문서를 속도로 이긴다", "의약품·식품 콜드체인(GDP)과 KC·CE·FCC 문서는 AI 초안이 가장 잘 먹히는 영역이다. 판정과 서명만 사람이 한다.", "W2·W4"),
    ("04", "기기에서 고객 화면까지 말하는 사람", "가전 H/W는 기기에서 끝난다. 로거 H/W는 서버·고객 리포트까지 이어진다. AI 덕에 넓어진 손으로 디바이스-클라우드 전체 구조를 설명할 수 있는 사람이 된다.", "W3·W4"),
]

w1, w2, w3, w4 = (S["by_wave"][k] for k in ("W1", "W2", "W3", "W4"))
st_fw = next(s for s in S["by_stage"] if s["stage"] == "펌웨어")
st_doc = next(s for s in S["by_stage"] if s["stage"] == "문서·협업")
st_pcb = next(s for s in S["by_stage"] if s["stage"] == "PCB·기구")

def exhibit(n, title, sub, body, src, sowhat):
    return f'''<section class="ex"><p class="exn">Exhibit {n}</p><h2>{title}</h2><p class="sub">{sub}</p>
<div class="chart">{body}</div><p class="src">{src}</p><div class="sw"><b>So what</b>{sowhat}</div></section>'''

SRC = "출처: H/W 개발 업무 48개 평가 데이터셋(본 분석의 가정 점수, 2026.11). 실측 설문이 아님."
road_html = "".join(f'''<div class="q"><div class="qh" style="border-color:{W[k]["color"]}"><span>{W[k]["q"]}</span><b>M{i + 1}. {title}</b></div>
<ul>{"".join(f"<li>{e(x)}</li>" for x in acts)}</ul><p class="kpi">KPI · {e(kpi)}</p></div>''' for i, (k, title, acts, kpi) in enumerate(ROAD))
strat_html = "".join(f'<div class="st"><span class="sn">{n}</span><div><h3>{h}</h3><p>{p}</p><p class="tag">연결 웨이브 {w}</p></div></div>' for n, h, p, w in STRAT)
table_rows = "".join(f'<tr><td>{e(r["stage"])}</td><td>{e(r["task"])}</td><td>{r["hours"]:g}</td><td>{r["cap25"]:g}</td><td>{r["cap27"]:g}</td><td>{r["err"]}</td><td>{r["verif"]}</td><td>{r["data"]}</td><td>{r["saved"]:.2f}</td><td><i style="background:{W[r["wave"]]["color"]}"></i>{W[r["wave"]]["en"]}</td></tr>' for r in ROWS)

CSS = """
:root{--navy:#051C2C;--blue:#2251FF;--cyan:#00A9F4;--ink:#1F2A33;--ink2:#4B5B67;--line:#D0D7DD;--bg:#fff;--soft:#F3F6F8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:'Noto Sans KR','Malgun Gothic',sans-serif;line-height:1.65;-webkit-text-size-adjust:100%}
.wrap{max-width:880px;margin:0 auto;padding:0 20px}
header{background:var(--navy);color:#fff;padding:44px 0 40px;position:relative;overflow:hidden}
header svg.lines{position:absolute;right:-40px;top:0;height:100%;opacity:.35}
.kick{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);margin:0 0 14px;font-weight:700}
h1{font-family:'Noto Serif KR',Georgia,serif;font-weight:700;font-size:clamp(28px,6vw,46px);line-height:1.25;margin:0 0 16px;max-width:680px}
.lede{font-size:16px;color:#C9D4DC;max-width:640px;margin:0}
.meta{font-size:12px;color:#8FA3B2;margin-top:22px}
nav{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);z-index:5}
nav .wrap{display:flex;gap:18px;overflow-x:auto;white-space:nowrap;padding-top:12px;padding-bottom:12px;font-size:13px}
nav a{color:var(--ink2);text-decoration:none}nav a:hover{color:var(--blue)}
.exec{padding:40px 0 10px}.exec h2{font-family:'Noto Serif KR',Georgia,serif;font-size:24px;margin:0 0 18px;color:var(--navy)}
.exec ol{padding-left:0;list-style:none;counter-reset:k;margin:0}
.exec li{counter-increment:k;position:relative;padding:14px 0 14px 46px;border-top:1px solid var(--line);font-size:16px}
.exec li:before{content:counter(k);position:absolute;left:0;top:13px;width:30px;height:30px;background:var(--blue);color:#fff;font-weight:700;display:grid;place-items:center;font-size:14px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin:30px 0 10px}
.kpis div{background:#fff;padding:18px 16px}.kpis b{display:block;font-family:'Noto Serif KR',Georgia,serif;font-size:32px;color:var(--navy);line-height:1.1}
.kpis b em{font-style:normal;color:var(--blue)}.kpis span{font-size:12.5px;color:var(--ink2)}
.ex{padding:44px 0 8px;border-top:1px solid var(--line);margin-top:30px}
.exn{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--blue);font-weight:700;margin:0 0 6px}
.ex h2,.sec h2{font-family:'Noto Serif KR',Georgia,serif;font-size:clamp(20px,4.2vw,26px);line-height:1.4;color:var(--navy);margin:0 0 6px}
.sub{color:var(--ink2);font-size:14px;margin:0 0 18px}
.chart{border-top:2px solid var(--navy);padding-top:14px}.chart svg{width:100%;height:auto;display:block}
.src{font-size:11.5px;color:#7A8A96;margin:10px 0 0}
.sw{background:var(--soft);border-left:4px solid var(--blue);padding:14px 18px;margin-top:16px;font-size:15px}.sw b{display:block;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--blue);margin-bottom:4px}
.sec{padding:48px 0 8px;border-top:1px solid var(--line);margin-top:30px}
.road{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-top:22px}
.q{border:1px solid var(--line);padding:18px}.qh{border-top:4px solid;padding-top:10px;margin:-18px -18px 10px;padding:12px 18px 0}
.qh span{display:block;font-size:12px;color:var(--ink2);font-weight:700;letter-spacing:.06em}.qh b{font-size:16.5px;color:var(--navy)}
.q ul{margin:8px 0;padding-left:18px;font-size:14.5px}.kpi{font-size:13px;color:var(--blue);font-weight:700;margin:8px 0 0;border-top:1px dashed var(--line);padding-top:8px}
.st{display:flex;gap:16px;border-top:1px solid var(--line);padding:18px 0}.sn{font-family:'Noto Serif KR',Georgia,serif;font-size:30px;color:var(--blue);font-weight:700;line-height:1;min-width:44px}
.st h3{margin:0 0 4px;font-size:17px;color:var(--navy)}.st p{margin:0;font-size:14.5px}.st .tag{font-size:12px;color:var(--ink2);margin-top:6px}
video{width:100%;display:block;background:#000;margin-top:18px}
.tbl{overflow-x:auto;margin-top:14px}table{border-collapse:collapse;font-size:12.5px;min-width:720px;width:100%}
th{background:var(--navy);color:#fff;font-weight:500;padding:8px 6px;text-align:left}td{border-bottom:1px solid var(--line);padding:6px}
td i{display:inline-block;width:9px;height:9px;margin-right:5px}
.method{font-size:14px;color:var(--ink2)}.method code{background:var(--soft);padding:2px 6px;font-size:13px}
.review{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:16px}.review div{border:1px solid var(--line);padding:14px;font-size:13.5px}
.review b{display:block;margin-bottom:4px}
footer{background:var(--navy);color:#8FA3B2;font-size:12px;padding:30px 0;margin-top:50px}
@media(max-width:640px){.kpis{grid-template-columns:repeat(2,1fr)}.road,.review{grid-template-columns:1fr}.kpis b{font-size:26px}.wrap{padding:0 16px}}
"""

LINES_SVG = '<svg class="lines" viewBox="0 0 400 300" fill="none" stroke="#00A9F4" stroke-width="1.2"><path d="M0 60h120l30 30h90l20-20h140M0 120h80l40 40h160M40 200h120l30-30h100l30 30h80M0 250h200l20 20h180"/><rect x="230" y="110" width="90" height="90"/><path d="M245 110v-14M265 110v-14M285 110v-14M305 110v-14M245 214v-14M265 214v-14M285 214v-14M305 214v-14"/><circle cx="150" cy="90" r="4"/><circle cx="120" cy="160" r="4"/><circle cx="160" cy="200" r="4"/></svg>'

page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>H/W × AI 로드맵 2027</title><meta name="description" content="H/W 개발 업무 48개 탐색적 데이터 분석으로 만든 2027 AI 협업 로드맵과 백색가전 대비 차별화 전략">
<meta property="og:title" content="H/W 개발자 × AI 협업 로드맵 2027"><meta property="og:description" content="48개 업무 EDA → 4개 웨이브 → 분기별 마일스톤">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header>{LINES_SVG}<div class="wrap"><p class="kick">Exploratory Data Analysis · H/W Engineering</p>
<h1>H/W 개발자의 AI 협업, 2027년엔 일의 {S["saved_pct"]}%를 맡기고 판단은 지킨다</h1>
<p class="lede">H/W 개발 업무 48개를 7개 변수로 점수화해 탐색적으로 분석했다. 결론은 네 개의 웨이브와 분기별 마일스톤, 그리고 백색가전 H/W 개발자와 다른 길이다.</p>
<p class="meta">2026년 11월 · 분석 단위: 주 {S["total_h"]:g}시간 업무 포트폴리오 · 5-Color 검토 반영</p></div></header>
<nav><div class="wrap"><a href="#sum">요약</a><a href="#ex1">단계별</a><a href="#ex3">상관</a><a href="#ex4">사분면</a><a href="#ex5">파레토</a><a href="#road">로드맵</a><a href="#diff">차별화</a><a href="#video">영상</a><a href="#method">방법론</a></div></nav>
<main class="wrap">
<section class="exec" id="sum"><h2>핵심 요약</h2>
<div class="kpis"><div><b>{S["n"]}</b><span>분석한 H/W 업무</span></div><div><b><em>{S["total_saved"]:g}</em>h</b><span>2027년 AI로 줄일 수 있는 주당 시간</span></div>
<div><b>{S["saved_pct"]}%</b><span>전체 업무 시간 중 비중</span></div><div><b>{S["top10_pct"]}%</b><span>상위 10개 업무가 차지하는 절감 몫</span></div></div>
<ol>
<li><b>AI 역량은 평균 {S["mean_cap25"]:.1f}점에서 {S["mean_cap27"]:.1f}점으로 오른다.</b> 하지만 상승은 고르지 않다. 문서·협업({st_doc["cap27"]:.1f}점)과 펌웨어({st_fw["cap27"]:.1f}점)가 앞서고, PCB·기구({st_pcb["cap27"]:.1f}점)는 뒤처진다.</li>
<li><b>AI가 잘하는 일은 데이터가 쌓인 일이다.</b> 2027 역량과 사내 데이터 준비도의 상관은 r={S["r_cap27_data"]:+.2f}, 오류 비용과는 r={S["r_cap27_err"]:+.2f}다. 데이터 준비도가 낮은 업무 {S["low_data_n"]}개의 2027 역량은 평균 {S["low_data_cap27"]:.1f}점에 그친다.</li>
<li><b>시간 절감은 몰려 있다.</b> 상위 10개 업무가 절감의 {S["top10_pct"]}%를 차지한다. 펌웨어 코드, 로그·측정 데이터 분석, 시험 코드가 1순위다.</li>
<li><b>그래서 2027년은 네 단계로 간다.</b> Q1 맡기기({w1["n"]}개), Q2 AI 초안과 사람 검증({w2["n"]}개), Q3 데이터 쌓기({w3["n"]}개), Q4 사람 판단 영역 명문화({w4["n"]}개)다.</li>
<li><b>백색가전과는 다른 길로 간다.</b> 규모와 기구로 정면 승부하지 않는다. 필드 데이터 루프, 전력 최적화, 규제 문서 속도, 디바이스-클라우드 통합으로 차별화한다.</li>
</ol></section>
<div id="ex1">{exhibit(1, f"펌웨어와 회로에 시간이 가장 많이 들고, AI 역량은 모든 단계에서 오르지만 PCB·기구가 가장 낮다", "단계별 주당 시간(왼쪽)과 평균 AI 역량 1~5점의 2025→2027 이동(오른쪽)", ex1(), SRC, f"시간이 많이 드는 펌웨어(주 {st_fw['hours']:g}h)는 2027 역량도 {st_fw['cap27']:.1f}점으로 높다. 가장 큰 절감 기회가 여기 있다. PCB·기구는 {st_pcb['cap27']:.1f}점이라 아직 'AI가 대신'이 아니라 'AI가 거든다'에 머문다.")}</div>
{exhibit(2, f"업무 {S['n']}개 중 {sum(c for u, c in S['uplift_hist'] if u >= 1.5)}개는 2년 사이 AI 역량이 1.5점 이상 오른다", "2025→2027 AI 역량 상승폭별 업무 수", ex2(), SRC, f"평균 상승폭은 +{S['mean_uplift']:.2f}점이다. 지금 역량이 낮은 업무일수록 덜 오른다(상관 r={S['r_uplift_cap25']:+.2f}). 그래서 격차는 저절로 줄지 않는다. 데이터를 쌓아야 줄어든다.")}
<div id="ex3">{exhibit(3, "AI 역량을 가장 잘 설명하는 변수는 '데이터 준비도'와 '오류 비용'이다", "7개 변수 피어슨 상관계수 (파랑 = 양, 빨강 = 음)", ex3(), SRC, f"2027 역량은 데이터 준비도(r={S['r_cap27_data']:+.2f}), 검증 용이성(r={S['r_cap27_verif']:+.2f})과 함께 오르고 오류 비용(r={S['r_cap27_err']:+.2f})과 반대로 간다. 개인이 바꿀 수 있는 레버는 데이터와 검증 방법이다.")}</div>
<div id="ex4">{exhibit(4, "48개 업무는 네 구역으로 갈린다. 오른쪽 위부터 맡기고, 왼쪽 아래는 사람이 지킨다", "x = 2027 AI 역량, y = 오류 비용(아래로 갈수록 위험), 원 크기 = 주당 시간. 점에 마우스를 올리면 업무명", ex4(), SRC + " 같은 점수의 업무는 겹치지 않게 조금 띄워 그렸다.", f"맡기기 구역 {w1['n']}개 업무가 주 {w1['hours']:g}h를 쓰고 그중 {w1['saved']:g}h를 줄일 수 있다. 사람이 지킬 구역(EMC, RF, ESD, OTA 등 {w4['n']}개)은 주 {w4['hours']:g}h로 크지만 절감은 {w4['saved']:g}h뿐이다. 여기는 AI보다 사람의 경험이 값이다.")}</div>
<div id="ex5">{exhibit(5, f"상위 10개 업무만 바꿔도 절감 가능 시간의 {S['top10_pct']}%를 얻는다", "업무별 2027 절감 가능 시간(막대, 색=웨이브)과 누적 비중(선)", ex5(), SRC + " 절감 시간 = 주당 시간 × 절감률(방법론 참조).", "1순위는 드라이버·HAL 코드, 디버깅·로그 분석, 측정 데이터 분석이다. 모두 펌웨어와 시험에 있다. 로드맵의 Q1·Q2가 이 업무들로 시작하는 이유다.")}</div>
<section class="sec" id="road"><p class="exn">Exhibit 6 · Roadmap</p><h2>2027년 로드맵: 분기마다 웨이브 하나, 마일스톤 하나</h2><p class="sub">사분면 분류가 그대로 순서가 된다. 위험이 낮고 효과가 큰 곳부터 시작하고, 위험한 곳은 마지막에 규칙으로 묶는다.</p>
<div class="chart">{ex6()}</div>
<div class="road">{road_html}</div>
<div class="sw"><b>명심할 것</b>AI는 '대신 일하는 사람'이 아니라 '초안을 빨리 쓰는 동료'다. 검증 체크리스트 없이 AI 결과를 회로·BOM·펌웨어에 넣지 않는다. 그리고 확보한 시간은 EMC·RF·안전 같은 사람 판단 영역에 다시 쓴다.</div></section>
<section class="sec" id="diff"><p class="exn">Exhibit 7 · Differentiation</p><h2>백색가전 H/W 개발자와 같은 길로 가지 않는다. 데이터·전력·속도에서 이긴다</h2>
<p class="sub">8개 축 비교. ○ 백색가전 H/W 개발 일반 프로파일, ● IoT 물류 로거 개발자의 2027 목표(가정 점수)</p>
<div class="chart">{ex7()}</div><p class="src">출처: 본 분석의 가정 점수. 특정 회사 평가가 아니라 업종 일반 프로파일 비교.</p>
<div class="sw"><b>So what</b>규모의 경제와 기구·안전 규격은 백색가전의 강점이라 정면 승부하지 않는다(회색). 대신 AI가 지렛대가 되는 네 축에 집중한다. 이 네 축은 앞의 EDA에서 AI 역량이 높게 나온 업무(로그 분석, 펌웨어, 문서)와 겹친다.</div>
{strat_html}</section>
<section class="sec" id="video"><p class="exn">Video · 60s</p><h2>1분 영상으로 보기</h2><p class="sub">키네틱 타이포그래피와 라인 아트, 한국어 내레이션</p>
<video controls playsinline preload="metadata" poster="poster.png" src="roadmap_2027.mp4"></video></section>
<section class="sec method" id="method"><p class="exn">Methodology</p><h2>방법론과 데이터</h2>
<p><b>데이터의 성격.</b> 공개 설문에는 H/W 업무 단위의 AI 적합도가 없다. 그래서 H/W 개발 8단계 48개 업무를 정의하고 7개 변수에 1~5점을 매긴 평가 데이터셋을 만들었다. 점수는 2025~2026년 AI 도구 동향을 바탕으로 한 <b>가정</b>이며 실측이 아니다. 숫자는 방향을 보는 용도로 읽어야 한다.</p>
<p><b>변수.</b> 주당 시간(h), AI 역량 2025·2027(1 못함 ~ 5 거의 대신함), 오류 비용(1 쉽게 되돌림 ~ 5 리콜·인증 실패), 검증 용이성(1 확인 어려움 ~ 5 자동 확인), 데이터 준비도(1 없음 ~ 5 정리됨).</p>
<p><b>절감률.</b> <code>0.75 × (역량2027−1)/4 × (1 − 0.15×(오류비용−1)) × (0.6 + 0.08×검증용이성)</code>. 최대 75%로 제한해 사람이 검토하는 시간을 남겼다.</p>
<p><b>웨이브 분류.</b> 역량2027 ≥ 3.5이고 오류비용 ≤ 2면 W1, 역량 ≥ 3.5이고 오류비용 ≥ 3이면 W2, 역량 &lt; 3.5이고 오류비용 ≤ 3이면 W3, 나머지는 W4다.</p>
<p><a href="data.csv">원자료 data.csv 내려받기</a> · 분석 코드 analyze.py · build_site.py</p>
<div class="tbl"><table><thead><tr><th>단계</th><th>업무</th><th>h/주</th><th>역량25</th><th>역량27</th><th>오류</th><th>검증</th><th>데이터</th><th>절감h</th><th>웨이브</th></tr></thead><tbody>{table_rows}</tbody></table></div>
<h2 style="margin-top:34px">5-Color 검토</h2>
<div class="review">
<div><b style="color:#E5546C">RED · 논리</b>가정 데이터임을 맨 앞과 모든 Exhibit 출처에 밝혔다. 모든 숫자는 data.csv에서 다시 계산된다.</div>
<div><b style="color:#8A9BA8">SILVER · H/W 전문가</b>EMC·RF·ESD·OTA·대체 부품 승인을 '사람이 지킨다'로 묶었다. 회로를 AI가 다 그린다는 과장은 없다.</div>
<div><b style="color:#00A9F4">BLUE · 공감</b>대체 공포 대신 '맡기고 지킨다'로 썼다. 확보한 시간을 사람 판단 영역에 다시 쓰는 것으로 끝난다.</div>
<div><b style="color:#C9A227">GOLD · 독자</b>출근길 3분 안에 핵심 요약 5줄과 KPI 4개, 분기별 할 일 4개를 가져갈 수 있다.</div></div>
</section></main>
<footer><div class="wrap">H/W × AI 협업 로드맵 2027 · 탐색적 데이터 분석 · 데이터는 가정 점수이며 투자·인사 판단의 근거가 아니다.</div></footer>
</body></html>"""
(OUT / "index.html").write_text(page, encoding="utf-8")
print("ok", len(page))
