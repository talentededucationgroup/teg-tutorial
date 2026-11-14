"""Prove the original 12g dialogue recordings are kept: locate each original dialogue segment inside the new file (FFT cross-correlation, 8 kHz)
and report the normalised correlation (1.0 = identical apart from MP3 re-encoding) plus its position; positions must be increasing (no swaps)."""
import json, subprocess, numpy as np, os, sys
S = os.path.dirname(os.path.abspath(__file__)); SR = 8000
SEG = json.load(open(S + '/p12/cd_segments.json'))
def pcm(p, a=None, b=None):
    c = ['ffmpeg', '-v', 'error'] + (['-ss', str(a)] if a is not None else []) + (['-to', str(b)] if b is not None else []) + ['-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.run(c, capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
def trim(x, thr=10 ** (-50 / 20)):
    i = np.where(np.abs(x) > thr)[0]; return x[i[0]:i[-1]]
res = {}
for s, v in SEG.items():
    out = pcm(S + f'/p12/final/{s}.mp3'); rows = []
    for it in v['items']:
        d = trim(pcm(S + f'/p12/orig/{s}.mp3', *it['dialog']))
        n = len(out) + len(d); N = 1 << (n - 1).bit_length()
        cc = np.fft.irfft(np.fft.rfft(out, N) * np.conj(np.fft.rfft(d, N)), N)[:len(out) - len(d) + 1]
        k = int(np.argmax(cc)); seg = out[k:k + len(d)]
        ncc = float(np.dot(seg, d) / (np.linalg.norm(seg) * np.linalg.norm(d) + 1e-9))
        rows.append({'n': it['n'], 'pos': round(k / SR, 2), 'dur': round(len(d) / SR, 2), 'ncc': round(ncc, 4)})
    order_ok = all(rows[i]['pos'] < rows[i + 1]['pos'] for i in range(len(rows) - 1))
    res[s] = {'items': rows, 'order_ok': order_ok, 'min_ncc': min(r['ncc'] for r in rows)}
    print(s, 'urutan OK' if order_ok else 'URUTAN SALAH', 'min ncc', res[s]['min_ncc'], [(r['n'], r['pos'], r['ncc']) for r in rows])
json.dump(res, open(S + '/audit8/dialog_identity.json', 'w'), indent=1)
