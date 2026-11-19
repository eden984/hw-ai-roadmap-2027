import asyncio, json, edge_tts, pathlib, subprocess, imageio_ffmpeg
D = pathlib.Path(__file__).parent
LINES = [
 "2027년, H/W 개발자는 AI와 어떻게 일해야 할까요? 업무 48개를 데이터로 분석했습니다.",
 "AI 역량은 평균 2.6점에서 3.8점으로 오릅니다. 그런데 AI가 잘하는 일은, 데이터가 쌓인 일입니다.",
 "업무는 네 구역으로 갈립니다. 상위 10개 업무만 바꿔도, 줄일 수 있는 시간의 45퍼센트를 얻습니다.",
 "1분기엔 맡기고, 2분기엔 AI 초안에 사람 검증을 붙이고, 3분기엔 데이터를 쌓고, 4분기엔 사람이 지킬 영역을 정합니다.",
 "백색가전과 같은 길로 가지 않습니다. 필드 데이터, 전력, 규제 문서 속도, 그리고 기기부터 클라우드까지에서 이깁니다.",
 "일의 34퍼센트는 AI에 맡기고, 판단은 우리가 지킵니다. H/W 곱하기 AI, 2027.",
]
async def main():
    ff = imageio_ffmpeg.get_ffmpeg_exe(); durs = []
    for i, s in enumerate(LINES):
        p = D / f"n{i}.mp3"
        await edge_tts.Communicate(s, "ko-KR-InJoonNeural", rate="+8%").save(str(p))
        out = subprocess.run([ff, "-i", str(p)], capture_output=True, text=True, encoding="utf-8", errors="ignore").stderr
        h, m, sec = out.split("Duration: ")[1].split(",")[0].split(":")
        durs.append(round(float(m) * 60 + float(sec), 2))
    json.dump(dict(lines=LINES, durs=durs), open(D / "narr.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(durs, sum(durs))
asyncio.run(main())
