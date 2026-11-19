"""키네틱 타이포 + 라인 아트 60초 영상. PIL 프레임 → ffmpeg 파이프."""
import json, math, pathlib, subprocess, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

D = pathlib.Path(__file__).parent; ROOT = D.parent
N = json.load(open(D / "narr.json", encoding="utf-8"))
ST = json.load(open(ROOT / "stats.json", encoding="utf-8"))
S, ROWS = ST["stats"], ST["rows"]
W, H, FPS = 1280, 720, 30
NAVY, BLUE, CYAN, WHITE, GREY, DIM = (5, 28, 44), (34, 81, 255), (0, 169, 244), (255, 255, 255), (138, 155, 168), (40, 70, 92)
F = "C:/Windows/Fonts/"
def font(name, size): return ImageFont.truetype(F + name, size)
KB = {s: font("malgunbd.ttf", s) for s in (22, 28, 34, 40, 48, 56, 64, 80)}
KR = {s: font("malgun.ttf", s) for s in (20, 24, 26, 30, 40)}
NUM = {s: font("georgiab.ttf", s) for s in (40, 90, 150, 220)}
WAVEC = {"W1": BLUE, "W2": CYAN, "W3": GREY, "W4": WHITE}

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def mix(c1, c2, a): return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))

def poly(d, pts, p, col, w=3):
    """폴리라인을 길이 비율 p만큼 그린다."""
    segs = list(zip(pts, pts[1:])); L = [math.dist(a, b) for a, b in segs]; tot = sum(L); left = tot * clamp(p)
    for (a, b), l in zip(segs, L):
        if left <= 0: break
        f = min(1, left / l) if l else 1
        d.line([a, (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)], fill=col, width=w); left -= l
    return tot

def text(d, xy, s, f, col, anchor="la", a=1.0):
    d.text(xy, s, font=f, fill=mix(NAVY, col, a), anchor=anchor)

def kin(d, x, y, s, f, col, t0, t, dy=40, anchor="la"):
    """아래에서 올라오며 나타나는 글자."""
    k = ease((t - t0) / 0.5)
    if k > 0: text(d, (x, y + dy * (1 - k)), s, f, col, anchor, k)

def words(d, x, y, ws, f, t0, t, gap=0.18, hl=()):
    """단어 단위 키네틱 타이포."""
    cx = x
    for i, w in enumerate(ws):
        col = BLUE if w in hl else WHITE
        k = ease((t - t0 - i * gap) / 0.45)
        wpx = d.textlength(w + " ", font=f)
        if k > 0:
            if w in hl and k >= 1:
                d.rectangle([cx - 6, y - 4, cx + d.textlength(w, font=f) + 6, y + f.size + 10], fill=BLUE); col = WHITE
            text(d, (cx, y + 30 * (1 - k)), w, f, col, a=k)
        cx += wpx

TRACES = [[(0, 120), (220, 120), (260, 160), (420, 160)], [(0, 600), (180, 600), (230, 550), (520, 550)],
          [(1280, 90), (1050, 90), (1010, 130), (860, 130)], [(1280, 640), (1100, 640), (1060, 600), (900, 600)],
          [(0, 360), (90, 360), (130, 320), (200, 320)], [(1280, 380), (1180, 380), (1150, 410), (1080, 410)]]
def traces(d, p, col=DIM):
    for i, tr in enumerate(TRACES):
        q = clamp(p * 1.4 - i * 0.07)
        poly(d, tr, q, col, 2)
        if q >= 1: x, y = tr[-1]; d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=col, width=2)

def chip(d, cx, cy, s, p, col=CYAN):
    r = s / 2
    poly(d, [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r), (cx - r, cy - r)], p, col, 3)
    for i in range(5):
        k = clamp(p * 2 - 1 - i * 0.08)
        if k > 0:
            x = cx - r + (i + 0.5) * s / 5
            d.line([x, cy - r, x, cy - r - 22 * k], fill=col, width=3); d.line([x, cy + r, x, cy + r + 22 * k], fill=col, width=3)
            y = cy - r + (i + 0.5) * s / 5
            d.line([cx - r, y, cx - r - 22 * k, y], fill=col, width=3); d.line([cx + r, y, cx + r + 22 * k, y], fill=col, width=3)

def subtitle(d, s, t, dur):
    a = clamp(t / 0.3) * clamp((dur - t) / 0.3)
    if a <= 0: return
    f = KR[40]; lines, cur = [], ""
    for w in s.split(" "):
        if d.textlength(cur + " " + w, font=f) > 1100 and cur: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    lines.append(cur)
    y0 = 650 - 52 * (len(lines) - 1)
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f); d.rectangle([640 - tw / 2 - 14, y0 + i * 52 - 6, 640 + tw / 2 + 14, y0 + i * 52 + 48], fill=(2, 14, 24))
        text(d, (640, y0 + i * 52), l, f, (220, 228, 235), "ma", a)

# ── 장면들 (t = 장면 안 시간)
def s0(d, t, dur):
    traces(d, t / 3, DIM); chip(d, 960, 330, 170, ease(t / 2.2))
    k = back((t - 0.4) / 0.8)
    if k > 0:
        f = NUM[220]; text(d, (110, 150 + (1 - k) * 60), "2027", f, WHITE, a=clamp(k))
    kin(d, 118, 410, "H/W 개발자 × AI 협업 로드맵", KB[48], CYAN, 1.3, t)
    if t > 4.6:
        n = int(S["n"] * ease((t - 4.6) / 1.4))
        text(d, (118, 490), f"{n}", NUM[90], WHITE); kin(d, 250, 520, "개 업무를 데이터로 분석", KB[40], WHITE, 4.8, t, 20)

def s1(d, t, dur):
    traces(d, 1, DIM)
    kin(d, 100, 80, "AI 역량 (1~5점)", KB[34], GREY, 0, t, 20)
    x0, x1 = 150, 1130; X = lambda v: x0 + (v - 1) / 4 * (x1 - x0)
    poly(d, [(x0, 250), (x1, 250)], ease(t / 1), DIM, 4)
    for v in range(1, 6):
        if t > 0.3 + v * 0.1: text(d, (X(v), 275), str(v), KR[24], GREY, "ma")
    p = ease((t - 1.2) / 2.2); a, b = S["mean_cap25"], S["mean_cap27"]; cur = a + (b - a) * p
    if t > 1:
        d.ellipse([X(a) - 14, 236, X(a) + 14, 264], outline=WHITE, width=4); text(d, (X(a), 190), f"2025  {a:.1f}", KB[28], WHITE, "ms")
    if t > 1.2:
        d.line([X(a), 250, X(cur), 250], fill=BLUE, width=8); d.ellipse([X(cur) - 18, 232, X(cur) + 18, 268], fill=BLUE)
        text(d, (X(cur), 210), f"{cur:.1f}", NUM[40], BLUE, "ms")
    words(d, 100, 400, ["AI가", "잘하는", "일은"], KB[56], 4.6, t)
    words(d, 100, 490, ["데이터가", "쌓인", "일이다"], KB[64], 5.4, t, hl=("데이터가",))
    if t > 7: kin(d, 820, 515, f"상관 r = {S['r_cap27_data']:+.2f}", KB[34], CYAN, 7, t, 15)

def s2(d, t, dur):
    X = lambda v: 140 + (v - 1.5) / 3.6 * 560; Y = lambda v: 50 + (v - 0.6) / 4.8 * 440
    poly(d, [(140, 500), (720, 500)], ease(t / 0.8), GREY, 2); poly(d, [(140, 500), (140, 40)], ease(t / 0.8), GREY, 2)
    poly(d, [(X(3.5), 40), (X(3.5), 500)], ease((t - 0.6) / 0.8), DIM, 2)
    seen = {}
    for i, r in enumerate(ROWS):
        k = back((t - 0.9 - i * 0.04) / 0.4)
        key = (r["cap27"], r["err"]); j = seen.get(key, 0); seen[key] = j + 1
        if k <= 0: continue
        ang = j * 2.4; rad = 0 if j == 0 else 9 + 3 * j
        cx, cy = X(r["cap27"]) + rad * math.cos(ang), Y(r["err"]) + rad * math.sin(ang)
        rr = (4 + math.sqrt(r["hours"]) * 6) * clamp(k, 0, 1.3)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=WAVEC[r["wave"]])
    text(d, (430, 512), "2027 AI 역량 →", KR[20], GREY, "ma")
    if t > 3.2:
        n = int(S["top10_pct"] * ease((t - 3.2) / 1.6))
        k = back((t - 3.2) / 0.7); text(d, (800, 170 + 40 * (1 - clamp(k))), f"{n}%", NUM[150], BLUE, a=clamp(k))
    kin(d, 806, 360, "상위 10개 업무가", KB[40], WHITE, 3.8, t, 20)
    kin(d, 806, 415, f"줄일 시간의 {S['top10_pct']}%", KB[40], WHITE, 4.3, t, 20)
    for i, (k_, lab) in enumerate([("W1", "맡긴다"), ("W2", "검증한다"), ("W3", "데이터부터"), ("W4", "지킨다")]):
        if t > 5.4 + i * 0.25:
            y = 490 + i * 0; x = 806 + i * 110; d.ellipse([x, 472, x + 16, 488], fill=WAVEC[k_]); text(d, (x + 22, 467), lab, KR[20], WHITE)

def s3(d, t, dur):
    traces(d, 1, DIM)
    kin(d, 100, 70, "2027 로드맵", KB[48], CYAN, 0, t, 20)
    y = 290; poly(d, [(110, y), (1170, y)], ease((t - 0.3) / 1.2), GREY, 4)
    items = [("Q1", "세운다", "안전 규칙·데이터·반복 업무", BLUE), ("Q2", "검증한다", "AI 초안 + 체크리스트", CYAN),
             ("Q3", "연결한다", "쌓은 데이터 → AI", GREY), ("Q4", "재투자", "확보한 시간을 판단으로", WHITE)]
    for i, (q, w, sub, col) in enumerate(items):
        t0 = 0.8 + i * (dur - 2.2) / 4; x = 210 + i * 287
        k = back((t - t0) / 0.5)
        if k <= 0: continue
        r = 22 * clamp(k, 0, 1.3); d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        text(d, (x, y - 50), q, NUM[40], col, "ms", clamp(k))
        kin(d, x, y + 50, w, KB[56], WHITE, t0 + 0.15, t, 30, "ma")
        kin(d, x, y + 125, sub, KR[24], GREY, t0 + 0.4, t, 15, "ma")

def s4(d, t, dur):
    traces(d, 1, DIM)
    a = clamp(t / 0.4) * (1 - ease((t - 1.8) / 0.6))
    if a > 0:
        text(d, (640, 160), "백색가전과 정면 승부?", KB[56], GREY, "ma", a)
        if t > 1.0:
            L = d.textlength("백색가전과 정면 승부?", font=KB[56]); d.line([640 - L / 2, 195, 640 - L / 2 + L * ease((t - 1) / 0.5), 195], fill=(229, 84, 108), width=6)
    # 로거 라인 아트
    p = ease((t - 2) / 1.5)
    if p > 0:
        cx, cy = 1040, 360
        poly(d, [(cx - 90, cy - 130), (cx + 90, cy - 130), (cx + 90, cy + 130), (cx - 90, cy + 130), (cx - 90, cy - 130)], p, CYAN, 4)
        poly(d, [(cx - 55, cy - 90), (cx + 55, cy - 90), (cx + 55, cy - 10), (cx - 55, cy - 10), (cx - 55, cy - 90)], clamp(p * 1.3 - 0.3), CYAN, 3)
        if p > 0.6: text(d, (cx, cy - 72), "-20.5°C", KB[28], WHITE, "ma", clamp((p - 0.6) * 2.5))
        for i in range(3):
            k = (t * 0.9 - i * 0.33) % 1
            if t > 3:
                rr = 30 + k * 90; d.arc([cx + 60 - rr, cy - 200 - rr, cx + 60 + rr, cy - 200 + rr], 220, 320, fill=mix(NAVY, CYAN, 1 - k), width=3)
        poly(d, [(cx + 60, cy - 130), (cx + 60, cy - 200)], p, CYAN, 4)
    items = ["필드 데이터 루프", "전력 최적화", "규제 문서 속도", "기기 → 클라우드"]
    for i, w in enumerate(items):
        t0 = 2.6 + i * 1.5; y = 250 + i * 85
        kin(d, 120, y, f"0{i + 1}", NUM[40], BLUE, t0, t, 25)
        kin(d, 200, y - 4, w, KB[56], WHITE, t0 + 0.1, t, 25)
    kin(d, 120, 600 - 40, "", KB[28], WHITE, 9, t)

def s5(d, t, dur):
    traces(d, ease(t / 2), DIM); chip(d, 640, 330, 120, ease(t / 1.5), DIM)
    k = back(t / 0.8)
    n = S["total_saved"] * ease(t / 1.6)
    if k > 0: text(d, (640, 110 + 40 * (1 - clamp(k))), f"{n:.1f}h", NUM[220], BLUE, "ma", clamp(k))
    words(d, 330, 400, ["반복은", "AI로", "덜고,"], KB[56], 1.6, t)
    words(d, 330, 475, ["그", "시간을", "판단에", "쓴다"], KB[64], 3.0, t, hl=("판단에",))
    if t > 6.3:
        a = ease((t - 6.3) / 0.6); d.rectangle([0, 0, W, H], fill=None)
        text(d, (640, 590 - 0), "H/W × AI  ·  2027", KB[34], CYAN, "ma", a)

SCENES = [s0, s1, s2, s3, s4, s5]
def main():
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    durs = N["durs"]; total = sum(durs) + 0.6
    # 오디오 이어 붙이기
    lst = D / "concat.txt"; lst.write_text("".join(f"file 'n{i}.mp3'\n" for i in range(6)), encoding="utf-8")
    subprocess.run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-af", "apad=pad_dur=0.6", "-c:a", "aac", "-b:a", "160k", str(D / "narr.m4a")], check=True)
    out = ROOT / "roadmap_2027.mp4"
    p = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(D / "narr.m4a"), "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
                          "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    nf = int(total * FPS); starts = [sum(durs[:i]) for i in range(6)]
    for fi in range(nf):
        T = fi / FPS
        si = max(i for i in range(6) if starts[i] <= T); t = T - starts[si]; dur = durs[si] if si < 5 else durs[5] + 0.6
        im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
        SCENES[si](d, t, dur)
        subtitle(d, N["lines"][si], t, dur)
        # 장면 전환 페이드
        fade = min(clamp(t / 0.25), clamp((dur - t) / 0.25)) if si < 5 else clamp(t / 0.25) * clamp((dur - t) / 0.5)
        if fade < 1: im = Image.blend(Image.new("RGB", (W, H), NAVY), im, fade)
        d.rectangle([0, H - 6, W * T / total, H], fill=BLUE)  # 진행 바
        if fi == int((starts[5] + 7.5) * FPS): im.save(ROOT / "poster.png")
        if fi % 300 == 0: print("frame", fi, "/", nf, flush=True)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); print("done", out, total)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:  # 미리보기: python render.py 장면 시간
        si, t = int(sys.argv[1]), float(sys.argv[2]); im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
        SCENES[si](d, t, N["durs"][si]); subtitle(d, N["lines"][si], t, N["durs"][si]); im.save(D / f"prev_{si}.png")
    else: main()
