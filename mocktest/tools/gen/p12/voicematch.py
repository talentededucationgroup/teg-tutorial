"""Rank candidate TTS voices by similarity to a reference clip (same text): MFCC + DTW distance, plus median F0."""
import subprocess, numpy as np, sys
SR = 16000
def load(p, a=None, b=None):
    c = ['ffmpeg', '-v', 'error'] + (['-ss', str(a)] if a is not None else []) + (['-to', str(b)] if b is not None else []) + ['-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-']
    x = np.frombuffer(subprocess.run(c, capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
    i = np.where(np.abs(x) > 0.01)[0]; return x[i[0]:i[-1]] if len(i) else x
def mel(n=26, nfft=512):
    f = lambda m: 700 * (10 ** (m / 2595) - 1); mm = np.linspace(0, 2595 * np.log10(1 + 8000 / 700), n + 2); hz = f(mm); bins = np.floor((nfft + 1) * hz / SR).astype(int)
    fb = np.zeros((n, nfft // 2 + 1))
    for i in range(1, n + 1):
        for k in range(bins[i - 1], bins[i]): fb[i - 1, k] = (k - bins[i - 1]) / max(1, bins[i] - bins[i - 1])
        for k in range(bins[i], bins[i + 1]): fb[i - 1, k] = (bins[i + 1] - k) / max(1, bins[i + 1] - bins[i])
    return fb
FB = mel()
def mfcc(x):
    n, h = 400, 160; w = np.hamming(n)
    fr = np.array([x[i:i + n] * w for i in range(0, len(x) - n, h)])
    P = np.abs(np.fft.rfft(fr, 512)) ** 2; E = np.log(P @ FB.T + 1e-10)
    k = np.arange(26); D = np.cos(np.pi / 26 * (k[:, None] + 0.5) * np.arange(1, 14)[None, :])
    C = E @ D; return (C - C.mean(0)) / (C.std(0) + 1e-6)
def dtw(a, b):
    n, m = len(a), len(b); d = np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1)); D = np.full((n + 1, m + 1), np.inf); D[0, 0] = 0
    for i in range(1, n + 1):
        for j in range(max(1, i - 200), min(m, i + 200) + 1):
            D[i, j] = d[i - 1, j - 1] + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    return D[n, m] / (n + m)
def f0(x):
    v = []
    for i in range(0, len(x) - 640, 160):
        s = x[i:i + 640] - x[i:i + 640].mean()
        if np.sqrt((s ** 2).mean()) < 0.03: continue
        ac = np.correlate(s, s, 'full')[639:]; lo, hi = SR // 400, SR // 70; k = lo + np.argmax(ac[lo:hi])
        if ac[k] > 0.4 * ac[0]: v.append(SR / k)
    return np.median(v) if v else 0
ref = load(*[sys.argv[1]] + [float(t) for t in sys.argv[2:4]]); R = mfcc(ref)
print(f'ref {len(ref)/SR:.2f}s f0 {f0(ref):.0f}')
for p in sys.argv[4:]:
    x = load(p); print(f'{p.split("/")[-1]:20} dur {len(x)/SR:.2f}s f0 {f0(x):4.0f}  dtw {dtw(R, mfcc(x)):.3f}')
