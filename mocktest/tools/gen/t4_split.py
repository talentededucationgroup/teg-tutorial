# Split grouped TTS files at long silences into per-item mp3 (mono 64 kbps).
import json, subprocess, re, sys, os
T = '/tmp/claude-0/-home-claude/7600d9ee-aee0-5a14-abd7-7540cbf5f3d4/scratchpad/pte'
import os as _o
OUT = _o.environ.get('OUT', '/home/claude/teg-tutorial/mocktest/audio/pte')
PRE = _o.environ.get('PRE', '')
FOLD = _o.environ.get('FOLD', 'mock-t4-pte')
os.makedirs(T, exist_ok=True)
G = json.load(open(_o.environ.get('GJ', '/home/claude/w91/t4_pte_groups.json')))
subprocess.run(['git', '-C', '/home/claude/teg-tutorial', 'fetch', '-q', 'origin', 'tts-audio:refs/remotes/origin/tts-audio'], check=True)
for gi in map(int, sys.argv[1:]):
    src = f'{T}/{PRE}G{gi}.mp3'
    open(src, 'wb').write(subprocess.run(['git', '-C', '/home/claude/teg-tutorial', 'show', f'origin/tts-audio:{FOLD}/{PRE}G{gi}.mp3'], capture_output=True, check=True).stdout)
    r = subprocess.run(['ffmpeg', '-i', src, '-af', 'silencedetect=noise=-45dB:d=' + _o.environ.get('SD','2.3'), '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r)]
    dur = float(re.search(r'Duration: (\d+):(\d+):([\d.]+)', r).group(3)) + 60 * int(re.search(r'Duration: (\d+):(\d+)', r).group(2))
    starts = [0.0] + en
    ids = G[gi]
    segs = []
    for i in range(len(ids)):
        a = max(0, starts[i] - 0.15) if i else 0.0
        b = (st[i] + 0.3) if i < len(st) else dur
        segs.append((a, b))
    print(f'G{gi}: items={len(ids)} silences={len(st)} dur={dur:.1f}')
    if len(st) < len(ids) - 1 or len(st) > len(ids):
        print('  MISMATCH', st); continue
    for iid, (a, b) in zip(ids, segs):
        dst = f'{OUT}/{iid}.mp3'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{a:.2f}', '-to', f'{b:.2f}', '-i', src, '-af', 'loudnorm=I=-18:TP=-2', '-ac', '1', '-ar', '24000', '-b:a', '64k', dst + '.tmp.mp3'], check=True)
        os.replace(dst + '.tmp.mp3', dst)
        print(f'  {iid} {b-a:.1f}s')
