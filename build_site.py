"""stats.json → 맥킨지 스타일 index.html (차트는 인라인 SVG)."""
import json, math, pathlib, html

OUT = pathlib.Path(__file__).parent
D = json.load(open(OUT / "stats.json", encoding="utf-8"))
S, ROWS = D["stats"], D["rows"]
W = S["waves"]
NAVY, BLUE, CYAN, GREY, LINE, INK2 = "#051C2C", "#2251FF", "#00A9F4", "#8A9BA8", "#D0D7DD", "#4B5B67"
e = html.escape
LEG = {"W1": "W1 · 바로 맡긴다(Q1부터)", "W2": "W2 · AI 초안 + 사람 검증(Q2부터)", "W3": "W3 · 데이터가 먼저(Q3 연결 후)", "W4": "W4 · 사람이 지킨다(연중)"}
SHORT = {"W1": "맡김", "W2": "초안+검증", "W3": "데이터 먼저", "W4": "사람이 지킴"}

def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}" xmlns="http://www.w3.org/2000/svg" font-family="Noto Sans KR, Malgun Gothic, sans-serif">{body}</svg>'

def t(x, y, s, size=13, fill=INK2, anchor="start", weight=400):
    size = max(size, 12)
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
        b.append(t(x, y + 4, LEG[k], 12, W[k]["color"] if k != "W3" else INK2, a, 700))
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
    b.append(f'<text x="18" y="200" font-size="13" fill="{NAVY}" font-weight="700" text-anchor="middle" transform="rotate(-90 18 200)">오류 비용 ↓(아래가 위험)</text>')
    return svg(720, 402, "".join(b), f"{S['n']}개 업무 사분면 산점도")

# Exhibit 5 — 파레토
def ex5():
    rk = sorted(ROWS, key=lambda r: -r["saved"])[:15]; tot = S["total_saved"]; mx = rk[0]["saved"]
    b, cum = [t(300, 16, "주당 절감 시간(h)", 12, NAVY, weight=700), t(700, 16, "누적 비중", 12, "#E5546C", "end", 700)], 0
    for i, r in enumerate(rk):
        y = 30 + i * 26; w = r["saved"] / mx * 300; cum += r["saved"]
        if i == 10: b.append(f'<line x1="0" y1="{y - 3}" x2="720" y2="{y - 3}" stroke="#E5546C" stroke-dasharray="4 3"/>')
        b.append(t(290, y + 15, r["task"], 12.5, NAVY, "end", 500))
        b.append(f'<rect x="300" y="{y + 3}" width="{w:.1f}" height="18" fill="{W[r["wave"]]["color"]}"/>')
        b.append(t(306 + w, y + 16, f'{r["saved"]:.2f}', 12, NAVY))
        b.append(t(700, y + 16, f'{round(100 * cum / tot)}%', 12.5, "#E5546C", "end", 700 if i == 9 else 400))
    b.append(t(700, 30 + 15 * 26 + 18, f'상위 10개 = 절감의 {S["top10_pct"]}%', 13, "#E5546C", "end", 700))
    return svg(720, 30 + 15 * 26 + 26, "".join(b), "절감 가능 시간 파레토")

# Exhibit 6 — 로드맵
ROAD = [
    ("W1", "안전장치를 먼저 세우고 맡기기 시작", ["사람 승인 필수 목록 확정: EMC·RF·안전·OTA·센서 교정·데이터 무결성(Part 11)", "사내 AI 보안 규칙: 회로도·소스·고객 데이터 업로드 범위", "회의록·보고서·번역·로그 분석부터 AI로 시작", "설계·시험·불량 이력 데이터 쌓기 시작(연중 계속)"], "보안 규칙 팀 합의 · 내가 고른 문서는 AI 초안으로 시작"),
    ("W2", "AI 초안 + 사람 검증 체계", ["회로·BOM·전원 계산에 검증 체크리스트 붙이기", "펌웨어는 AI 작성 → 리뷰 → 테스트 통과만 병합", "측정 데이터 분석·단종 부품 모니터링 자동화"], "AI 산출물로 인한 설계 결함 0건 · Q1 평균 대비 PR당 리뷰 시간 30%↓ (Q1에 기준값 측정)"),
    ("W3", "쌓은 데이터를 AI에 연결", ["Q1부터 모은 시험·불량·설계 결정 기록을 한 저장소로", "AI 사내 지식 검색 시범 운영", "데이터 준비도 낮은 업무(SPICE·수율 등)부터 적용"], "데이터 먼저 업무 중 2개 이상 데이터 준비도 +1점 · 필드 로그 분석 시간 Q1 기준값 대비 50%↓"),
    ("W4", "점검하고 다시 투자", ["사람 승인 목록·보안 규칙 1년 점검", "확보한 시간을 EMC·RF·교정 같은 판단 업무에 재배치", "2028 계획 수립"], "확보 시간의 절반 이상을 판단 업무에 재투자"),
]
def ex6():
    b = []
    for i in range(4):
        x = 190 + i * 130
        b.append(f'<rect x="{x}" y="10" width="126" height="26" fill="{NAVY}"/>'); b.append(t(x + 63, 28, f"2027 Q{i + 1}", 13, "#fff", "middle", 700))
    bars = [("안전·보안 규칙", "Q1 세우고 연중 운영", 0, 0, "#E5546C"), ("데이터 쌓기", "Q1 시작, 연중 계속", 0, 2, GREY),
            ("맡기기", "반복 업무부터", 0, 0, BLUE), ("AI 초안 + 검증", "설계·펌웨어로 확대", 1, 1, CYAN),
            ("사내 데이터 연결", "지식 검색 가동", 2, 2, "#5B6B78"), ("점검·재투자", "2028 계획", 3, 3, NAVY)]
    for i, (lab, sub, st_, solid, col) in enumerate(bars):
        y = 48 + i * 44; x = 190 + st_ * 130
        b.append(t(0, y + 18, lab, 14, NAVY, weight=700)); b.append(t(0, y + 35, sub, 11.5, INK2))
        b.append(f'<rect x="{x}" y="{y + 6}" width="{714 - x}" height="30" fill="{col}" fill-opacity=".22"/>')
        sw = 190 + (solid + 1) * 130 - x - 4
        b.append(f'<rect x="{x}" y="{y + 6}" width="{sw}" height="30" fill="{col}"/>')
    b.append(t(190, 48 + 6 * 44 + 14, "진한 칸 = 집중 실행 분기, 연한 칸 = 이후 계속 운영", 11.5, GREY))
    return svg(720, 48 + 6 * 44 + 22, "".join(b), "2027 분기별 로드맵")

# Exhibit 7 — 백색가전 대비 차별화
def ex7():
    b = []; X = lambda v: 250 + (v - 1) * 110
    b.append(t(0, 16, "○ 백색가전 H/W 2027 일반 전망   ● IoT 물류 로거 H/W 2027 목표", 12, NAVY, weight=700))
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
    ("01", "필드 데이터 루프 엔지니어", "가전도 연결 데이터를 모은다. 다른 점은 로거는 데이터 자체가 고객에게 파는 상품이라는 것이다. AI로 필드 로그를 분석해 불량 징후를 찾는 시간을 줄인다(목표: Q3에 필드 로그 분석 소요 시간을 Q1 기준값의 절반으로). 펌웨어 배포는 고객의 변경 관리 주기를 따른다.", "W1·W2"),
    ("02", "전력 예산의 주인", "로거는 배터리 하나로 몇 달을, 그것도 영하 수십 도에서 버틴다. AI로 소비전류 프로파일을 자동 분석하고 배터리 수명을 예측하는 능력을 개인 무기로 만든다.", "W2"),
    ("03", "규제 문서는 속도가 무기다", "의약품·식품 콜드체인(GDP)과 KC·CE·FCC 문서는 AI 초안 효과가 큰 영역이다. 다만 판정·서명과 데이터 무결성(Part 11)은 사람이 지킨다.", "W2·W4"),
    ("04", "기기에서 고객 화면까지 말하는 사람", "가전은 기기 완성도가 승부처고, 로거는 기기와 데이터가 함께 승부처다. AI 덕에 넓어진 손으로 디바이스-클라우드 전체 구조를 설명할 수 있는 사람이 된다.", "W2"),
]

w1, w2, w3, w4 = (S["by_wave"][k] for k in ("W1", "W2", "W3", "W4"))
st_fw = next(s for s in S["by_stage"] if s["stage"] == "펌웨어")
st_doc = next(s for s in S["by_stage"] if s["stage"] == "문서·협업")
st_pcb = next(s for s in S["by_stage"] if s["stage"] == "PCB·기구")

def exhibit(n, title, sub, body, src, sowhat):
    return f'''<section class="ex"><p class="exn">Exhibit {n}</p><h2>{title}</h2><p class="sub">{sub}</p>
<p class="hint">← 차트를 옆으로 밀어 보세요</p><div class="chart">{body}</div><p class="tip" hidden></p><p class="src">{src}</p><div class="sw"><b>시사점</b>{sowhat}</div></section>'''

SRC = f"출처: H/W 개발 업무 {S['n']}개 평가 데이터셋(본 분석의 가정 점수, 2026.11). 실측 설문이 아님."
road_html = "".join(f'''<div class="q"><div class="qh" style="border-color:{W[k]["color"]}"><span>{W[k]["q"]}</span><b>M{i + 1}. {title}</b></div>
<ul>{"".join(f"<li>{e(x)}</li>" for x in acts)}</ul><p class="kpi">KPI · {e(kpi)}</p></div>''' for i, (k, title, acts, kpi) in enumerate(ROAD))
strat_html = "".join(f'<div class="st"><span class="sn">{n}</span><div><h3>{h}</h3><p>{p}</p><p class="tag">연결 웨이브 {w}</p></div></div>' for n, h, p, w in STRAT)
table_rows = "".join(f'<tr><td>{e(r["stage"])}</td><td>{e(r["task"])}</td><td>{r["hours"]:g}</td><td>{r["cap25"]:g}</td><td>{r["cap27"]:g}</td><td>{r["err"]}</td><td>{r["verif"]}</td><td>{r["data"]}</td><td>{r["saved"]:.2f}</td><td><i style="background:{W[r["wave"]]["color"]}"></i>{SHORT[r["wave"]]}</td></tr>' for r in ROWS)

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
.next{border:2px solid var(--blue);padding:16px 18px;margin-top:22px}.next b{color:var(--blue);font-size:15px}.next ol{margin:8px 0 0;padding-left:20px;font-size:15px}
.tip{font-size:14px;color:var(--navy);background:var(--soft);padding:8px 12px;margin:8px 0 0}
details summary{cursor:pointer;color:var(--blue);font-weight:700;margin-top:10px}
.rv{border-collapse:collapse;font-size:14px;min-width:0;width:100%}.rv td,.rv th{padding:8px;border-bottom:1px solid var(--line);text-align:left}
.ans{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin-top:16px}.an{display:block;border:1px solid var(--line);border-top:4px solid var(--blue);padding:14px;text-decoration:none;color:var(--ink)}.an b{display:block;font-family:"Noto Serif KR",Georgia,serif;font-size:28px;color:var(--navy)}.an span{display:block;font-size:14px}.an em{display:block;font-style:normal;color:var(--blue);font-size:13px;margin-top:6px;font-weight:700}.an small{display:block;color:#7A8A96;font-size:11.5px;margin-top:6px}
.go{display:inline-block;margin-top:12px;background:var(--blue);color:#fff;padding:9px 16px;text-decoration:none;font-weight:700;font-size:14px}
.hint{display:none;font-size:12px;color:var(--ink2);margin:0 0 4px}
@media(max-width:640px){.chart{overflow-x:auto}.chart svg{min-width:720px}.hint{display:block}.ex{display:flex;flex-direction:column}.ex .sw{order:-1;margin:0 0 14px}.ex .exn{order:-3}.ex h2{order:-3}.ex .sub{order:-2}#road .hint,.ganttc{display:none}.kpis{grid-template-columns:repeat(2,1fr)}.road,.review{grid-template-columns:1fr}.kpis b{font-size:26px}.wrap{padding:0 16px}}
"""

LINES_SVG = '<svg class="lines" viewBox="0 0 400 300" fill="none" stroke="#00A9F4" stroke-width="1.2"><path d="M0 60h120l30 30h90l20-20h140M0 120h80l40 40h160M40 200h120l30-30h100l30 30h80M0 250h200l20 20h180"/><rect x="230" y="110" width="90" height="90"/><path d="M245 110v-14M265 110v-14M285 110v-14M305 110v-14M245 214v-14M265 214v-14M285 214v-14M305 214v-14"/><circle cx="150" cy="90" r="4"/><circle cx="120" cy="160" r="4"/><circle cx="160" cy="200" r="4"/></svg>'

AN = json.load(open(OUT / "anchors.json", encoding="utf-8"))
anchor_html = "".join(f'<a class="an" href="{a['url']}" target="_blank" rel="noopener"><b>{a['num']}</b><span>{e(a['text'])}</span><em>{e(a['use'])}</em><small>{e(a['src'])} ↗</small></a>' for a in AN)
REVIEW = (OUT / "review.html").read_text(encoding="utf-8")
R3 = json.load(open(OUT / "review3.json", encoding="utf-8")) if (OUT / "review3.json").exists() else {}
for k in ("RED", "SILVER", "BLUE", "GOLD", "ALL"): REVIEW = REVIEW.replace("{R3_" + k + "}", str(R3.get(k, "진행 중")))
REVIEW = REVIEW.replace("{R3_NOTE}", R3.get("note", ""))
NARR = "".join(f"<li>{e(x)}</li>" for x in json.load(open(OUT / "video" / "narr.json", encoding="utf-8"))["lines"])
page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>H/W × AI 로드맵 2027</title><meta name="description" content="H/W 개발 업무 {S["n"]}개 탐색적 데이터 분석으로 만든 2027 AI 협업 로드맵과 백색가전 대비 차별화 전략">
<meta property="og:title" content="H/W 개발자 × AI 협업 로드맵 2027"><meta property="og:description" content="{S["n"]}개 업무 EDA → 4개 웨이브 → 분기별 마일스톤">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header>{LINES_SVG}<div class="wrap"><p class="kick">탐색적 데이터 분석 · H/W 엔지니어링</p>
<h1>2027년, 반복 업무 주 {S["total_saved"]:g}시간을 AI로 덜고 그 시간을 판단에 쓴다</h1>
<p class="lede">IoT 물류 로거 업무를 포함한 H/W 개발 업무 {S["n"]}개를 7개 변수로 점수화해 탐색적으로 분석했다. 결론은 네 개의 웨이브와 분기별 마일스톤, 그리고 백색가전 H/W 개발자와 다른 길이다.</p>
<p class="meta">2026년 11월 · 분석 단위: 연간 업무량을 주 {S["total_h"]:g}시간으로 환산한 업무 포트폴리오 · 5-Color 검토 반영</p></div></header>
<nav><div class="wrap"><a href="#sum">요약</a><a href="#ext">외부 지표</a><a href="#ex1">단계별</a><a href="#ex3">상관</a><a href="#ex4">사분면</a><a href="#ex5">파레토</a><a href="#road">로드맵</a><a href="#diff">차별화</a><a href="#video">영상</a><a href="#method">방법론</a></div></nav>
<main class="wrap">
<section class="exec" id="sum"><h2>핵심 요약</h2>
<div class="kpis"><div><b>{S["n"]}</b><span>분석한 H/W 업무</span></div><div><b><em>{S["total_saved"]:g}</em>h</b><span>2027년 AI로 줄일 수 있는 주당 시간</span></div>
<div><b>{S["saved_pct"]}%</b><span>전체 업무 시간 중 비중</span></div><div><b>{S["top10_pct"]}%</b><span>상위 10개 업무가 차지하는 절감 몫</span></div></div>
<ol>
<li><b>AI 역량은 평균 {S["mean_cap25"]:.1f}점에서 {S["mean_cap27"]:.1f}점으로 오른다.</b> 하지만 상승은 고르지 않다. 문서·협업({st_doc["cap27"]:.1f}점)과 펌웨어({st_fw["cap27"]:.1f}점)가 앞서고, PCB·기구({st_pcb["cap27"]:.1f}점)는 뒤처진다.</li>
<li><b>가정 점수상 AI 역량은 데이터가 쌓인 일에서 높다.</b> 2027 역량과 사내 데이터 준비도의 상관은 r={S["r_cap27_data"]:+.2f}, 오류 비용과는 r={S["r_cap27_err"]:+.2f}다. 데이터 준비도가 낮은 업무 {S["low_data_n"]}개의 2027 역량은 평균 {S["low_data_cap27"]:.1f}점에 그친다.</li>
<li><b>시간 절감은 몰려 있다.</b> 상위 10개 업무가 절감의 {S["top10_pct"]}%를 차지한다. 펌웨어 코드, 로그·측정 데이터 분석, 시험 코드가 1순위다.</li>
<li><b>안전장치와 데이터부터 시작한다.</b> Q1에 사람 승인 목록·보안 규칙을 세우고 데이터 쌓기를 시작하면서 반복 업무({w1["n"]}개)를 맡긴다. Q2 AI 초안과 사람 검증({w2["n"]}개), Q3 쌓은 데이터 연결, Q4 점검과 재투자로 넓힌다. 끝까지 사람이 지킬 업무는 {w4["n"]}개다.</li>
<li><b>백색가전과는 다른 길로 간다.</b> 가전의 강점인 규모와 기구로 정면 승부하지 않는다. 필드 데이터 루프, 전력 최적화, 규제 문서 속도, 디바이스-클라우드 통합으로 차별화한다.</li>
</ol>
<div class="next"><b>다음 주 바로 해볼 3가지</b><ol><li>지난주 시험 로그 하나를 AI에 넣고 분석 스크립트를 받아 직접 돌려 보기</li><li>데이터시트 1개의 핀맵을 AI로 요약하고 원본과 한 줄씩 대조하기</li><li>회의록 1건을 AI로 정리하기 (고객·회로 정보는 사내 규칙 확인 뒤)</li></ol><a class="go" href="#road">2027 로드맵 바로 보기 →</a></div></section>
<section class="sec" id="ext"><p class="exn">Exhibit 0 · 외부 지표</p><h2>바깥 데이터가 먼저 말한다: AI 도입은 기본값이고, 신뢰는 아직 아니다</h2>
<p class="sub">업무별 점수를 증명하지는 않지만, 이 로드맵의 전제(도입은 기본, 신뢰는 아직)를 받치는 공개 통계 4개. 카드를 누르면 원문이 열린다.</p><div class="ans">{anchor_html}</div>
<div class="sw"><b>시사점</b>AI 사용은 84~89%로 높고(84%는 계획 포함) 정확도 신뢰는 33%로 낮다. 이 간극이 이 로드맵의 출발점이다. AI를 쓸지는 이미 정해졌고, 어떻게 검증하고 어디까지 맡길지가 남았다.</div></section>
<div id="ex1">{exhibit(1, f"펌웨어와 회로에 시간이 가장 많이 들고, AI 역량은 모든 단계에서 오르지만 PCB·기구가 가장 낮다", "단계별 주당 시간(왼쪽)과 평균 AI 역량 1~5점의 2025→2027 이동(오른쪽)", ex1(), SRC, f"시간이 많이 드는 펌웨어(주 {st_fw['hours']:g}h)는 2027 역량도 {st_fw['cap27']:.1f}점으로 높다. 가장 큰 절감 기회가 여기 있다. PCB·기구는 {st_pcb['cap27']:.1f}점이라 아직 'AI가 대신'이 아니라 'AI가 거든다'에 머문다.")}</div>
{exhibit(2, f"업무 {S['n']}개 중 {sum(c for u, c in S['uplift_hist'] if u >= 1.5)}개는 2년 사이 AI 역량이 1.5점 이상 오른다", "2025→2027 AI 역량 상승폭별 업무 수", ex2(), SRC, f"평균 상승폭은 +{S['mean_uplift']:.2f}점이다. 지금 역량이 낮은 업무일수록 더 많이 오른다(r={S['r_uplift_cap25']:+.2f}). 격차는 줄지만 사라지지 않는다. 데이터 준비도가 낮은 업무 {S['low_data_n']}개는 2027년에도 평균 {S['low_data_cap27']:.1f}점에 머문다.")}
<div id="ex3">{exhibit(3, "가정 점수상 2027 AI 역량은 데이터 준비도와 함께 오르고 오류 비용과 반대로 간다", "7개 변수 피어슨 상관계수 (파랑 = 양, 빨강 = 음)", ex3(), SRC, f"2027 역량은 데이터 준비도(r={S['r_cap27_data']:+.2f}), 검증 용이성(r={S['r_cap27_verif']:+.2f})과 함께 오르고 오류 비용(r={S['r_cap27_err']:+.2f})과 반대로 간다. 같은 평가자가 매긴 점수끼리의 관계라 독립된 증거는 아니지만, 개인이 움직일 수 있는 레버가 데이터와 검증 방법이라는 것은 이 분석의 가정이며, Q3 KPI로 검증한다.")}</div>
<div id="ex4">{exhibit(4, f"{S['n']}개 업무는 네 구역으로 갈린다. 오른쪽 위부터 맡기고, 왼쪽 아래는 사람이 지킨다", "x = 2027 AI 역량, y = 오류 비용(아래로 갈수록 위험), 원 크기 = 주당 시간. 점을 누르면 아래에 업무명이 뜬다", ex4(), SRC + " 같은 점수의 업무는 겹치지 않게 조금 띄워 그렸다.", f"맡기기 구역 {w1['n']}개 업무가 주 {w1['hours']:g}h를 쓰고 그중 {w1['saved']:g}h를 줄일 수 있다. 사람이 지킬 구역(EMC, RF, ESD, OTA, 센서 교정 등 {w4['n']}개)은 주 {w4['hours']:g}h로 크지만 절감은 {w4['saved']:g}h뿐이다. 여기는 AI보다 사람의 경험이 값이다.")}</div>
<div id="ex5">{exhibit(5, f"상위 10개 업무만 바꿔도 절감 가능 시간의 {S['top10_pct']}%를 얻는다", "상위 15개 업무의 2027 절감 가능 시간(막대, 색=웨이브)과 누적 비중(오른쪽)", ex5(), SRC + " 절감 시간 = 주당 시간 × 절감률(방법론 참조).", "1순위는 드라이버·HAL 코드, 디버깅·로그 분석, 자동 시험 스크립트다. 모두 펌웨어와 시험에 있다. 로그 분석·시험 스크립트는 Q1부터 맡기고, 드라이버·HAL 코드는 Q2에 'AI 초안 + 리뷰 + 테스트' 체계로 넣는 이유다.")}</div>
<section class="sec" id="road"><p class="exn">Exhibit 6 · 로드맵</p><h2>2027년 로드맵: 안전장치와 데이터가 먼저, 맡기는 범위는 분기마다 넓힌다</h2><p class="sub">안전·보안 규칙과 데이터 쌓기는 Q1에 시작해 1년 내내 돌리고, AI에 맡기는 범위는 분기마다 넓힌다.</p>
<p class="hint">← 차트를 옆으로 밀어 보세요</p><div class="chart ganttc">{ex6()}</div>
<div class="road">{road_html}</div>
<div class="sw"><b>명심할 것</b>AI는 '대신 일하는 사람'이 아니라 '초안을 빨리 쓰는 동료'다. 검증 체크리스트 없이 AI 결과를 회로·BOM·펌웨어에 넣지 않는다. 그리고 확보한 시간은 EMC·RF·안전 같은 사람 판단 영역에 다시 쓴다.</div></section>
<section class="sec" id="diff"><p class="exn">Exhibit 7 · 차별화</p><h2>백색가전 H/W 개발자와 다른 길을 간다. 데이터·전력·속도가 우리 무대다</h2>
<p class="sub">8개 축 비교. 두 쪽 모두 2027년 기준이다. ○ 백색가전 H/W 일반 전망, ● IoT 물류 로거 H/W의 목표(가정 점수)</p>
<p class="hint">← 차트를 옆으로 밀어 보세요</p><div class="chart">{ex7()}</div><p class="src">출처: 본 분석의 가정 점수. 특정 회사 평가가 아니라 업종 일반 프로파일 비교.</p>
<div class="sw"><b>시사점</b>규모의 경제와 기구·안전 규격은 백색가전의 강점이라 정면 승부하지 않는다(회색). 대신 로거만의 네 축에 집중한다. 01 필드 데이터와 03 규제 문서는 EDA에서 AI 역량이 높게 나온 로그 분석·문서 업무가 받친다. 02 전력과 04 디바이스-클라우드는 AI가 거들 뿐, 사람의 설계 역량이 핵심이다.</div>
{strat_html}</section>
<section class="sec" id="video"><p class="exn">영상 · 60초</p><h2>1분 영상으로 보기</h2><p class="sub">키네틱 타이포그래피와 라인 아트, 한국어 내레이션</p>
<video controls playsinline preload="metadata" poster="poster.png" src="roadmap_2027.mp4"></video><details><summary>소리 없이 보기: 내레이션 6줄</summary><ol>{NARR}</ol></details></section>
<section class="sec method" id="method"><p class="exn">방법론</p><h2>방법론과 데이터</h2>
<p><b>데이터의 성격.</b> 공개 설문에는 H/W 업무 단위의 AI 적합도가 없다. 그래서 H/W 개발 8단계 {S["n"]}개 업무(IoT 로거 고유 업무 7개 포함)를 정의하고 7개 변수에 1~5점을 매긴 평가 데이터셋을 만들었다. 점수는 2025~2026년 AI 도구 동향을 바탕으로 한 <b>가정</b>이며 실측이 아니다. 숫자는 방향을 보는 용도로 읽어야 한다.</p>
<p><b>변수.</b> 주당 시간(h), AI 역량 2025·2027(1 못함 ~ 5 거의 대신함), 오류 비용(1 쉽게 되돌림 ~ 5 리콜·인증 실패), 검증 용이성(1 확인 어려움 ~ 5 자동 확인), 데이터 준비도(1 없음 ~ 5 정리됨).</p>
<p><b>업무 시간.</b> 한 사람이 모든 업무를 매주 다 하는 것이 아니라, 연간 업무량을 주 단위로 환산한 값이다.</p>
<p><b>상관의 한계.</b> 모든 점수를 같은 평가자가 매겼으므로 상관은 독립된 증거가 아니라 평가 가정이 드러난 것이다.</p>
<p><b>절감률.</b> <code>0.75 × (역량2027−1)/4 × (1 − 0.15×(오류비용−1)) × (0.6 + 0.08×검증용이성)</code>. 최대 75%로 제한해 사람이 검토하는 시간을 남겼다.</p>
<p><b>웨이브 분류.</b> 오류비용이 5(리콜·인증 실패 수준)면 역량과 관계없이 W4다. 나머지는 역량2027 ≥ 3.5이고 오류비용 ≤ 2면 W1, 역량 ≥ 3.5이고 오류비용 3~4면 W2, 역량 &lt; 3.5이고 오류비용 ≤ 3이면 W3, 그 밖은 W4다.</p>
<p><b>외부 지표.</b> Exhibit 0의 숫자는 원문 페이지에서 확인했다. RunSafe 조사는 표본이 약 200명으로 작고, Black Duck·RunSafe는 원 보고서가 아닌 공식 블로그·보도 페이지 기준이다.</p>
<p><a href="data.csv">원자료 data.csv 내려받기</a> · 분석 코드 analyze.py · build_site.py</p>
<details><summary>업무 {S["n"]}개 원자료 표 펼치기</summary><div class="tbl"><table><thead><tr><th>단계</th><th>업무</th><th>h/주</th><th>역량25</th><th>역량27</th><th>오류</th><th>검증</th><th>데이터</th><th>절감h</th><th>웨이브</th></tr></thead><tbody>{table_rows}</tbody></table></div></details>
<h2 style="margin-top:34px">5-Color 검토</h2>{REVIEW}
</section></main>
<footer><div class="wrap">H/W × AI 협업 로드맵 2027 · 탐색적 데이터 분석 · 데이터는 가정 점수이며 투자·인사 판단의 근거가 아니다.</div></footer>
<script>document.querySelectorAll('.chart circle').forEach(c=>{{const tt=c.querySelector('title');if(!tt)return;c.style.cursor='pointer';c.addEventListener('click',()=>{{const tip=c.closest('section').querySelector('.tip');if(tip){{tip.hidden=false;tip.textContent='● '+tt.textContent}}}})}})</script>
</body></html>"""
(OUT / "index.html").write_text(page, encoding="utf-8")
print("ok", len(page))
