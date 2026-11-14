"""FINAL version: narrator clips from TEG_TTS (Azure). JLPT c/d: ja-JP-NanamiNeural (= voice of the original c/d labels); HSK c/d: zh-CN-YunyangNeural (= 12g HSK a/b narrator; labels re-voiced so one narrator per file; female voices rendered 女的 like 你的).
P1/P2 (owner decision 13/11): add narrator questions to the ORIGINAL 12g dialogue-only c/d recordings.
JLPT c/d: intro + per item [original label] [question] [original dialogue] [question]   (format of 12g a/b sets)
HSK c/d:  per item [original label] [original dialogue] [问：question]                  (official HSK: question after dialogue; played once - no 2x, P5 not approved)
Sources: original audio = 838677d; intro = 12g L5a/L4a narrator; question clips = narrator TTS clips (SRC_Q), gain-matched to the original file.
Output: MP3 mono 48 kHz 64 kbps."""
import json, re, subprocess, os, sys, numpy as np
S = os.path.dirname(os.path.abspath(__file__)); A = '/home/claude/teg-tutorial/mocktest/'
SR = 48000
OUT = os.environ.get('OUT', S + '/p12/out'); os.makedirs(OUT, exist_ok=True)
SEG = json.load(open(S + '/p12/cd_segments.json'))
V2 = json.load(open(S + '/p12/v2_chunks.json'))
def pcm(p, a=None, b=None):
    cmd = ['ffmpeg', '-v', 'error'] + (['-ss', str(a)] if a is not None else []) + (['-to', str(b)] if b is not None else []) + ['-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
def lufs(x):
    p = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', 'ebur128', '-f', 'null', '-'], input=x.astype(np.float32).tobytes(), capture_output=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', p.stderr.decode())[-1])
def trim(x, thr=10 ** (-50 / 20), pad=0.12):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx): return x
    a = max(0, idx[0] - int(pad * SR)); b = min(len(x), idx[-1] + int(pad * SR)); return x[a:b]
def sil(t): return np.zeros(int(t * SR), np.float32)
def fade(x, t=0.01):
    n = min(int(t * SR), len(x) // 2); w = np.linspace(0, 1, n, dtype=np.float32); x = x.copy(); x[:n] *= w; x[-n:] *= w[::-1]; return x
def v2_items(s, long_gap):
    ch = [c for c in V2[s] if c[1] - c[0] > 0.1]; items = []; cur = []
    for c in ch:
        cur.append(c)
        if c[2] >= long_gap: items.append(cur); cur = []
    if cur: items.append(cur)
    return items
def q_clips(s):
    """question clips from the v2 narrator file: JLPT -> (q_before, q_after); HSK -> 问+question (first play)."""
    p = S + f'/p12/v2/{s}.mp3'
    if s[0] == 'L':
        its = v2_items(s, 3.0); out = []
        for it in its:
            out.append((trim(pcm(p, it[1][0] - 0.2, it[1][1] + 0.1), pad=0.15), trim(pcm(p, it[-1][0] - 0.2, it[-1][1] + 0.1), pad=0.15)))
        return out
    out = []
    for it in v2_items(s, 3.0):          # one item = first play + second play
        it = [c for c in it if c[1] - c[0] > 0.1]
        k = next(i for i, c in enumerate(it) if c[2] >= 1.8)   # end of the first play
        first = it[:k + 1]; assert len(first) >= 4, (s, first)
        out.append(trim(pcm(p, max(0, first[-2][0] - 0.25), first[-1][1] + 0.1), pad=0.15))   # '问' + question
    return out
TTS = S + '/p12/tts/'; TZH = S + '/p12/tts_zh/'
def q_tts(s):
    n = len(SEG[s]['items'])
    if s[0] == 'L': return [(trim(pcm(TTS + f'{s}_{k}.mp3')),) * 2 for k in range(1, n + 1)]
    return [trim(pcm(TZH + f'{s}_{k}.mp3')) for k in range(1, n + 1)]
def build(s):
    src = S + '/p12/orig/' + s + '.mp3'  # original 12g recording (838677d)
    orig = pcm(src); target = lufs(orig)
    items = SEG[s]['items']; Q = q_tts(s); assert len(Q) == len(items), (s, len(Q), len(items))
    def match(x): g = target - lufs(x); return fade(x * (10 ** (g / 20)))
    parts = []; log = []
    if s[0] == 'L':
        intro = trim(pcm(TTS + 'ja_intro.mp3'))  # 'もんだい。はなしを きいて、しつもんに こたえて ください。' (Nanami)
        parts += [match(intro), sil(2.2)]; log.append('intro')
    for k, it in enumerate(items):
        lab = trim(orig[int(it['label'][0] * SR):int(it['label'][1] * SR)]) if s[0] == 'L' else match(trim(pcm(TZH + f"lab_{it['n']}.mp3")))
        dlg = trim(orig[int(it['dialog'][0] * SR):int(it['dialog'][1] * SR)])
        tail = it['dialog'][1] - it['dialog'][0] - len(dlg) / SR  # original pause after the dialogue
        if s[0] == 'L':
            qb, qa = Q[k]
            parts += [lab, sil(1.0), match(qb), sil(1.9), dlg, sil(1.4), match(qa), sil(5.5 if k + 1 < len(items) else 1.5)]
        else:
            parts += [lab, sil(0.7), dlg, sil(1.2), match(Q[k]), sil(max(3.0, min(tail, 5.0)) if k + 1 < len(items) else 1.5)]
        log.append(k + 1)
    y = np.concatenate(parts); y = np.clip(y, -1, 1)
    o = f'{OUT}/{s}.mp3'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '64k', '-ac', '1', '-ar', str(SR), o], input=y.tobytes(), check=True)
    print(s, f'{len(orig) / SR:.1f}s -> {len(y) / SR:.1f}s', f'orig {target:.1f} LUFS, out {lufs(y):.1f} LUFS', log, flush=True)
for s in (sys.argv[1:] or SEG): build(s)
