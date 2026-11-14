"""Find per-item boundaries in the original (12g) dialogue-only c/d audio: label ('Nばん。'/'第N题。') and dialogue spans.
Cut points are placed at the middle of detected silences next to the ASR-located labels."""
import json, re, subprocess, os, numpy as np
from faster_whisper import WhisperModel
S = os.path.dirname(os.path.abspath(__file__)); A = '/home/claude/teg-tutorial/mocktest/'
m = WhisperModel(S + '/asrmodels/medium', device='cpu', compute_type='int8', cpu_threads=2)
SETS = {'L5c': 'ja', 'L5d': 'ja', 'L4c': 'ja', 'L4d': 'ja', 'H1Lc': 'zh', 'H1Ld': 'zh', 'H2Lc': 'zh', 'H2Ld': 'zh', 'H3Lc': 'zh', 'H3Ld': 'zh'}
def path(s): return A + ('audio/jlpt/' if s[0] == 'L' else 'audio/hsk/') + s + '.mp3'
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
def silences(p):
    e = subprocess.run(['ffmpeg', '-v', 'info', '-i', p, '-af', 'silencedetect=n=-45dB:d=0.25', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', e)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', e)]
    return list(zip(st, en))
NUM = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5}
out = {}
for s, lang in SETS.items():
    p = path(s); D = dur(p); sil = silences(p)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    segs, _ = m.transcribe(x, language=lang, beam_size=5, condition_on_previous_text=False, word_timestamps=True)
    words = [(w.start, w.end, w.word) for sg in segs for w in sg.words]
    labs = []  # (n, index of first label word, index of last label word)
    i = 0
    while i < len(words):
        txt = ''.join(w for _, _, w in words[i:i + 4])
        mm = re.match(r'\s*(?:第\s*([一二三四五1-5])\s*[题題]|([1-5一二三四五])\s*(?:番|ばん))', txt)
        if mm and (not labs or labs[-1][0] != NUM[mm.group(1) or mm.group(2)]):
            n = NUM[mm.group(1) or mm.group(2)]; acc = ''; j = i
            while j < len(words):
                acc += words[j][2]
                if re.search(r'[题題番]|ばん', acc): break
                j += 1
            while j + 1 < len(words) and re.fullmatch(r'\s*[。.、,，]\s*', words[j + 1][2]): j += 1
            labs.append((n, i, j)); i = j + 1; continue
        i += 1
    def mid_sil(a, b):
        c = [z for z in sil if z[1] > a and z[0] < b]
        if c: z = max(c, key=lambda z: min(z[1], b) - max(z[0], a)); return (max(z[0], a) + min(z[1], b)) / 2
        return (a + b) / 2
    items = []
    for k, (n, i0, i1) in enumerate(labs):
        st = 0.0 if i0 == 0 else mid_sil(words[i0 - 1][1], words[i0][0])
        le = mid_sil(words[i1][1], words[i1 + 1][0]) if i1 + 1 < len(words) else D
        nxt = mid_sil(words[labs[k + 1][1] - 1][1], words[labs[k + 1][1]][0]) if k + 1 < len(labs) else D
        items.append({'n': n, 'label': [round(st, 3), round(le, 3)], 'dialog': [round(le, 3), round(nxt, 3)]})
    out[s] = {'dur': D, 'items': items, 'labels_found': [n for n, _, _ in labs]}
    print(s, round(D, 1), [n for n, _, _ in labs], [(i['label'], i['dialog']) for i in items], flush=True)
json.dump(out, open(S + '/p12/cd_segments.json', 'w'), indent=1)
