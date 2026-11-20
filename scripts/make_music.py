#!/usr/bin/env python3
# Jalankan: python3 scripts/make_music.py (menulis .wav ke folder kerja; ubah ke mp3 dengan ffmpeg loudnorm -16 LUFS)
# Musik latar orisinal Talented (dibuat dengan sintesis, tanpa sampel pihak ketiga) - bebas dipakai untuk promosi.
import numpy as np, scipy.signal as sg, scipy.io.wavfile as wf, sys
SR=44100
def n2f(n): return 440*2**((n-69)/12)
def env(t,a,d,s,r,L):
    e=np.ones_like(t)*s
    e[t<a]=t[t<a]/a
    m=(t>=a)&(t<a+d); e[m]=1-(1-s)*(t[m]-a)/d
    rr=t>L-r; e[rr]*=np.clip((L-t[rr])/r,0,1); return e
def tone(f,L,kind='saw',a=.01,d=.2,s=.6,r=.2,det=0):
    t=np.arange(int(L*SR))/SR
    if kind=='saw': w=sum(np.sin(2*np.pi*f*k*t*(1+det))/k for k in range(1,12))*.5
    elif kind=='pluck': w=sum(np.sin(2*np.pi*f*k*t)/k**1.6 for k in range(1,8))
    elif kind=='bell': w=np.sin(2*np.pi*f*t)+.35*np.sin(2*np.pi*f*2.76*t)*np.exp(-3*t)
    else: w=np.sin(2*np.pi*f*t)
    return w*env(t,a,d,s,r,L)
def lp(x,fc): b,a=sg.butter(2,fc/(SR/2)); return sg.lfilter(b,a,x)
def kick(L=.35):
    t=np.arange(int(L*SR))/SR; f=50+90*np.exp(-30*t); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-8*t)
def hat(L=.06):
    t=np.arange(int(L*SR))/SR; n=np.random.randn(len(t)); b,a=sg.butter(2,7000/(SR/2),'high'); return sg.lfilter(b,a,n)*np.exp(-60*t)*.3
def clap(L=.2):
    t=np.arange(int(L*SR))/SR; n=np.random.randn(len(t)); b,a=sg.butter(2,[1200/(SR/2),5000/(SR/2)],'band'); return sg.lfilter(b,a,n)*np.exp(-18*t)*.5
def track(name,bpm,root,prog,style,bars=8,seed=1):
    np.random.seed(seed); beat=60/bpm; bar=4*beat; L=bars*bar+1.5; out=np.zeros(int(L*SR)); st=np.zeros_like(out)
    def add(x,t0,g=1,pan=0):
        i=int(t0*SR); j=min(len(out),i+len(x)); out[i:j]+=x[:j-i]*g*(1-pan); st[i:j]+=x[:j-i]*g*(1+pan)
    for b in range(bars):
        ch=prog[b%len(prog)]; notes=[root+ch[0],root+ch[1],root+ch[2]]; t0=b*bar
        for k,nn in enumerate(notes):  # pad
            add(lp(tone(n2f(nn),bar+.3,'saw',a=.4,d=.5,s=.7,r=.6,det=.002*k),1800),t0,.05,pan=(k-1)*.4)
        add(tone(n2f(root+ch[0]-12),bar,'sine',a=.02,d=.3,s=.8,r=.2),t0,.28)  # bass
        arp=notes+[notes[1]+12]
        for s16 in range(16 if style!='calm' else 8):
            step=bar/(16 if style!='calm' else 8); nn=arp[s16%4]+(12 if style=='bright' and s16%8>=4 else 0)
            add(tone(n2f(nn+12),step*1.6,'pluck' if style!='calm' else 'bell',a=.005,d=.15,s=.15,r=.1),t0+s16*step,.07,pan=.3*np.sin(s16))
        if style!='calm' and 1<=b<bars-1:
            for q in range(4):
                add(kick(),t0+q*beat,.5)
                add(hat(),t0+q*beat+beat/2,.6,pan=.2)
                if q in (1,3): add(clap(),t0+q*beat,.35)
    mix=np.stack([out,st],1); mix=lp(mix.T,12000).T
    mix/=np.max(np.abs(mix))+1e-9; mix*=.9
    fade=int(1.2*SR); mix[-fade:]*=np.linspace(1,0,fade)[:,None]; mix[:int(.05*SR)]*=np.linspace(0,1,int(.05*SR))[:,None]
    wf.write(name+'.wav',SR,(mix*32767).astype(np.int16))
I,V,vi,IV,ii,iii=[0,4,7],[7,11,14],[9,12,16],[5,9,12],[2,5,9],[4,7,11]
PROGS=[[I,V,vi,IV],[vi,IV,I,V],[I,iii,IV,V],[I,IV,vi,V],[IV,V,iii,vi],[I,vi,IV,V],[ii,V,I,vi],[I,V,IV,IV],[vi,V,IV,V],[IV,I,V,vi]]
STYLES=['bright','pop','calm','bright','pop']
if __name__=='__main__':
    import random,sys
    n=int(sys.argv[1]) if len(sys.argv)>1 else 20
    for k in range(1,n+1):
        r=random.Random(1000+k)
        st=r.choice(STYLES);bpm=r.choice([78,84,90,96,100,104,108,112,116,120,124]) if st!='calm' else r.choice([72,76,80,84])
        track(f'talented-{st}-{k:02d}',bpm,r.choice([55,57,58,60,62,63,65]),r.choice(PROGS),st,8 if st!='calm' else 6,1000+k)
