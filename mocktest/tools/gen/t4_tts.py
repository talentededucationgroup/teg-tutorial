# Build listening audio from per-line TTS clips (cheaper than SSML).
# plan:  python3 t4_tts.py plan <bank-module> <folder>     -> prints generate_chapters batches (voice -> chapters)
# build: python3 t4_tts.py build <bank-module> <folder> <outdir>
import json, sys, os, subprocess, importlib, re, html
sys.path.insert(0, '/home/claude/w91')
import t4_common as C

def lines(mod):
    importlib.import_module(mod)
    out = []  # (sid, [(voice, fname, text, pause_after_ms)])
    for k, (sid, v) in enumerate(C.AUD.items()):
        lang, items, qt = v
        m, f = C.VOICES[lang][k % len(C.VOICES[lang])]
        nar = C.NAR[lang]
        seq = []
        for i, d in enumerate(items, 1):
            qq = qt[i - 1] if i - 1 < len(qt) else ''
            seq.append((nar, f'{sid}_{i}q', C.LAB[lang].format(i) + qq, 700))
            for j, (s, t) in enumerate(d):
                seq.append((m if s == 'M' else f, f'{sid}_{i}_{j}', t, 500))
            seq.append((nar, f'{sid}_{i}q', None, 2500))  # question repeated (same clip)
        out.append((sid, seq))
    return out

if __name__ == '__main__':
    cmd, mod, folder = sys.argv[1:4]
    L = lines(mod)
    if cmd == 'plan':
        by = {}
        for sid, seq in L:
            for v, fn, t, p in seq:
                if t: by.setdefault(v, []).append({'filename': fn + '.mp3', 'text': t})
        for v, ch in by.items():
            for i in range(0, len(ch), 20):
                print(json.dumps({'voice': v, 'chapters': ch[i:i + 20]}, ensure_ascii=False))
    else:
        outdir = sys.argv[4]; os.makedirs(outdir, exist_ok=True)
        tmp = '/tmp/claude-0/-home-claude/7600d9ee-aee0-5a14-abd7-7540cbf5f3d4/scratchpad/tts_' + folder
        os.makedirs(tmp, exist_ok=True)
        subprocess.run(['git', '-C', '/home/claude/teg-tutorial', 'fetch', '-q', 'origin', 'tts-audio:refs/remotes/origin/tts-audio'], check=True)
        for sid, seq in L:
            parts = []
            for n, (v, fn, t, p) in enumerate(seq):
                src = f'{tmp}/{fn}.mp3'
                if not os.path.exists(src):
                    data = subprocess.run(['git', '-C', '/home/claude/teg-tutorial', 'show', f'origin/tts-audio:{folder}/{fn}.mp3'], capture_output=True, check=True).stdout
                    open(src, 'wb').write(data)
                parts.append((src, p))
            # concat with silences
            inputs, flt = [], ''
            for n, (src, p) in enumerate(parts):
                inputs += ['-i', src]
                flt += f'[{n}:a]aresample=24000,aformat=channel_layouts=mono,apad=pad_dur={p/1000}[a{n}];'
            flt += ''.join(f'[a{n}]' for n in range(len(parts))) + f'concat=n={len(parts)}:v=0:a=1,loudnorm=I=-18:TP=-2[o]'
            dst = f'{outdir}/{sid}.mp3'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', flt, '-map', '[o]', '-ac', '1', '-ar', '24000', '-b:a', '64k', dst + '.tmp.mp3'], check=True)
            os.replace(dst + '.tmp.mp3', dst)
            print(sid, os.path.getsize(dst))
