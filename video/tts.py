import asyncio, json, edge_tts, pathlib, subprocess, imageio_ffmpeg
D = pathlib.Path(__file__).parent
S = json.load(open(D.parent / "stats.json", encoding="utf-8"))["stats"]
LINES = [
 f"2027년, H/W 개발자는 AI와 어떻게 일해야 할까요? 로거 업무를 포함해 업무 {S['n']}개를 데이터로 분석했습니다.",
 f"가정 점수로 본 AI 역량은 평균 {S['mean_cap25']}점에서 {S['mean_cap27']}점으로 오릅니다. 그리고 AI가 잘하는 일은, 데이터가 쌓인 일입니다.",
 f"업무는 네 구역으로 갈립니다. 상위 10개 업무만 바꿔도, 줄일 수 있는 시간의 {S['top10_pct']}퍼센트를 얻습니다.",
 "1분기엔 안전 규칙과 데이터부터 세우고, 2분기엔 AI 초안에 사람 검증을, 3분기엔 데이터를 연결하고, 4분기엔 점검해 다시 투자합니다.",
 "백색가전과 정면 승부하지 않습니다. 필드 데이터, 전력, 규제 문서 속도, 그리고 기기부터 클라우드까지가 우리 무대입니다.",
 f"반복 업무 주 {S['total_saved']:g}시간은 AI로 덜고, 그 시간을 판단에 씁니다. H/W 곱하기 AI, 2027.",
]
async def main():
    ff = imageio_ffmpeg.get_ffmpeg_exe(); durs = []
    for i, s in enumerate(LINES):
        p = D / f"n{i}.mp3"
        await edge_tts.Communicate(s, "ko-KR-InJoonNeural", rate="+14%").save(str(p))
        out = subprocess.run([ff, "-i", str(p)], capture_output=True, text=True, encoding="utf-8", errors="ignore").stderr
        h, m, sec = out.split("Duration: ")[1].split(",")[0].split(":")
        durs.append(round(float(m) * 60 + float(sec), 2))
    json.dump(dict(lines=LINES, durs=durs), open(D / "narr.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(durs, sum(durs))
asyncio.run(main())
