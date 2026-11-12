# Simple flat situation illustrations (Talented-made) for JLPT 発話表現. 640x360 SVG, no text.
W, H, G = 640, 360, 332
SKIN = '#f2c9a0'
def rect(x, y, w, h, f, rx=0, extra=''): return f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' fill='{f}' {extra}/>"
def circ(x, y, r, f, extra=''): return f"<circle cx='{x}' cy='{y}' r='{r}' fill='{f}' {extra}/>"
def line(x1, y1, x2, y2, c, w=9): return f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{c}' stroke-width='{w}' stroke-linecap='round'/>"
def path(d, f, extra=''): return f"<path d='{d}' fill='{f}' {extra}/>"

def person(x, g='M', shirt='#3a7bd5', pants='#34495e', pose='down', kind='adult', sit=False, s=1.0, gy=G):
    o = []
    k = s
    top = gy - (205 if not sit else 160) * k
    hy = top + 26 * k            # head centre
    by0, by1 = hy + 26 * k, hy + 26 * k + 78 * k   # body top/bottom
    if sit:
        o.append(rect(x - 14 * k, by1 - 6, 50 * k, 16 * k, pants, 8))           # thigh forward
        o.append(rect(x + 26 * k, by1 - 4, 14 * k, gy - by1 + 4, pants, 6))     # shin
    else:
        o.append(rect(x - 15 * k, by1 - 8, 12 * k, gy - by1 + 8, pants, 5))
        o.append(rect(x + 3 * k, by1 - 8, 12 * k, gy - by1 + 8, pants, 5))
        o.append(rect(x - 18 * k, gy - 6, 16 * k, 8, '#2b2b2b', 4)); o.append(rect(x + 2 * k, gy - 6, 16 * k, 8, '#2b2b2b', 4))
    if kind == 'pajama': shirt = pants = '#9fb8e6'
    o.append(rect(x - 27 * k, by0, 54 * k, by1 - by0, shirt, 16 * k))
    if kind == 'clerk': o.append(rect(x - 20 * k, by0 + 22 * k, 40 * k, by1 - by0 - 10 * k, '#ffffff', 6, "stroke='#ccc'"))
    sx, sy = 25 * k, by0 + 12 * k
    arms = {'down': [(-sx, sy, -sx - 8 * k, sy + 55 * k), (sx, sy, sx + 8 * k, sy + 55 * k)],
            'wave': [(-sx, sy, -sx - 8 * k, sy + 55 * k), (sx, sy, sx + 28 * k, sy - 45 * k)],
            'point': [(-sx, sy, -sx - 8 * k, sy + 55 * k), (sx, sy, sx + 55 * k, sy + 5 * k)],
            'pointl': [(-sx, sy, -sx - 55 * k, sy + 5 * k), (sx, sy, sx + 8 * k, sy + 55 * k)],
            'hold': [(-sx, sy, -sx + 18 * k, sy + 38 * k), (sx, sy, sx - 18 * k, sy + 38 * k)],
            'holdr': [(-sx, sy, -sx - 8 * k, sy + 55 * k), (sx, sy, sx + 45 * k, sy + 25 * k)],
            'holdl': [(-sx, sy, -sx - 45 * k, sy + 25 * k), (sx, sy, sx + 8 * k, sy + 55 * k)],
            'up': [(-sx, sy, -sx - 6 * k, sy - 50 * k), (sx, sy, sx + 6 * k, sy - 50 * k)],
            'fan': [(-sx, sy, -sx - 8 * k, sy + 55 * k), (sx, sy, sx + 22 * k, sy - 30 * k)],
            'palms': [(-sx, sy, -6 * k, sy + 26 * k), (sx, sy, 6 * k, sy + 26 * k)]}[pose]
    for ax, ay, bx, by in arms:
        o.append(line(x + ax, ay, x + bx, by, shirt, 11 * k)); o.append(circ(x + bx, by, 6 * k, SKIN))
    hair = '#2d2018' if kind != 'old' else '#c9c9c9'
    if g == 'F': o.append(path(f"M{x-28*k},{hy+30*k} Q{x-34*k},{hy-30*k} {x},{hy-30*k} Q{x+34*k},{hy-30*k} {x+28*k},{hy+30*k} Z", hair))
    o.append(circ(x, hy, 24 * k, SKIN))
    if g == 'M': o.append(path(f"M{x-25*k},{hy-2*k} Q{x-24*k},{hy-30*k} {x},{hy-28*k} Q{x+26*k},{hy-30*k} {x+25*k},{hy-2*k} Q{x+10*k},{hy-16*k} {x-25*k},{hy-2*k} Z", hair))
    else: o.append(path(f"M{x-24*k},{hy-4*k} Q{x},{hy-34*k} {x+24*k},{hy-4*k} Q{x+4*k},{hy-14*k} {x-24*k},{hy-4*k} Z", hair))
    o.append(circ(x - 8 * k, hy + 3 * k, 2.6 * k, '#222')); o.append(circ(x + 8 * k, hy + 3 * k, 2.6 * k, '#222'))
    o.append(path(f"M{x-6*k},{hy+12*k} Q{x},{hy+17*k} {x+6*k},{hy+12*k}", 'none', "stroke='#8a4b2f' stroke-width='2' stroke-linecap='round'"))
    if kind in ('teacher', 'old'):
        o.append(circ(x - 8 * k, hy + 3 * k, 6.5 * k, 'none', "stroke='#333' stroke-width='2'")); o.append(circ(x + 8 * k, hy + 3 * k, 6.5 * k, 'none', "stroke='#333' stroke-width='2'"))
    if kind == 'old': o.append(line(x + 40 * k, by0 + 50 * k, x + 46 * k, gy, '#7a5230', 5))
    if kind == 'sick': pass
    return ''.join(o), top

def arrow(x, top):
    y = top - 58
    return f"<g fill='#d62828'><rect x='{x-7}' y='{y}' width='14' height='26' rx='3'/><polygon points='{x-20},{y+24} {x+20},{y+24} {x},{y+48}'/></g>"

def room(wall='#f6efe3', floor='#d9c3a0'): return rect(0, 0, W, H, wall) + rect(0, G, W, H - G, floor)
def door(x, w=110, open_=True, out='#bfe3ff'):
    s = rect(x, 96, w, G - 96, '#8a5a35', 4) + rect(x + 8, 104, w - 16, G - 104, out if open_ else '#a8744a', 2)
    return s + (rect(x + w - 26, 215, 8, 18, '#e9c46a', 3) if not open_ else '')
def window(x, y, w, h, sky='#bfe3ff'): return rect(x, y, w, h, '#ffffff', 6) + rect(x + 7, y + 7, w - 14, h - 14, sky, 3) + line(x + w / 2, y + 7, x + w / 2, y + h - 7, '#ffffff', 5)
def table(x, w, y=262, c='#a0694a'): return rect(x, y, w, 14, c, 4) + rect(x + 12, y + 14, 10, G - y - 14, c) + rect(x + w - 22, y + 14, 10, G - y - 14, c)
def desk(x, w=150, y=250): return table(x, w, y, '#8d6748')
def board(x=40, y=50, w=250, h=120): return rect(x, y, w, h, '#2f5d46', 6, "stroke='#8a5a35' stroke-width='8'")
def boxgift(x, y, s=34): return rect(x, y, s, s, '#e76f51', 4) + rect(x + s / 2 - 4, y, 8, s, '#f4d35e') + rect(x, y + s / 2 - 4, s, 8, '#f4d35e')
def bag(x, y): return rect(x, y, 34, 40, '#6d4c41', 6) + path(f"M{x+8},{y} Q{x+17},{y-16} {x+26},{y}", 'none', "stroke='#6d4c41' stroke-width='4'")
def train(): return rect(0, 0, W, H, '#e9eef2') + rect(0, 60, W, 110, '#cfd8dc') + ''.join(window(30 + i * 150, 70, 120, 80, '#a8d8ff') for i in range(4)) + ''.join(line(80 + i * 120, 0, 80 + i * 120, 40, '#90a4ae', 4) + circ(80 + i * 120, 50, 11, 'none', "stroke='#90a4ae' stroke-width='4'") for i in range(5)) + rect(0, G, W, H - G, '#b0bec5')
def bench(x, w): return rect(x, 262, w, 22, '#4f7cac', 8) + rect(x, 228, w, 34, '#5d8fc4', 8)
def street(sky='#cfe8ff'): return rect(0, 0, W, H, sky) + rect(0, 120, 130, 212, '#d7ccc8') + rect(150, 70, 120, 262, '#bcaaa4') + rect(500, 100, 140, 232, '#d7ccc8') + ''.join(rect(20 + 30 * i, 140 + 40 * j, 18, 22, '#ffffff') for i in range(3) for j in range(4)) + rect(0, G, W, H - G, '#9e9e9e')
def bowl(x, y): return path(f"M{x-28},{y} Q{x},{y+34} {x+28},{y} Z", '#c0392b') + path(f"M{x-24},{y} Q{x},{y-18} {x+24},{y} Z", '#ffffff') + line(x + 18, y - 26, x + 40, y - 6, '#8d6e63', 4)
def bed(x, w=260): return rect(x, 240, w, 40, '#ffffff', 8, "stroke='#b0bec5' stroke-width='3'") + rect(x, 280, w, 16, '#90a4ae') + rect(x + w - 16, 190, 16, 106, '#90a4ae', 4)
def monitor(x, y): return rect(x, y, 70, 46, '#37474f', 4) + rect(x + 5, y + 5, 60, 36, '#80cbc4') + rect(x + 30, y + 46, 10, 10, '#37474f')
def apples(x, y): return rect(x, y + 14, 90, 26, '#a1887f', 4) + ''.join(circ(x + 15 + 20 * i, y + 12, 11, '#e53935') for i in range(4))
def sun(x, y): return circ(x, y, 26, '#ffca28') + ''.join(line(x, y, x + dx, y + dy, '#ffca28', 4) for dx, dy in ((0, -44), (0, 44), (-44, 0), (44, 0), (31, 31), (-31, -31), (31, -31), (-31, 31)))
def rain(): return ''.join(line(20 + (i * 53) % 620, (i * 37) % 300, 12 + (i * 53) % 620, (i * 37) % 300 + 22, '#5c8fd6', 3) for i in range(60))
def umbrella(x, top): return path(f"M{x-60},{top-10} Q{x},{top-80} {x+60},{top-10} Z", '#ef476f') + line(x, top - 40, x, top + 70, '#555', 4)
def cam(x, y): return rect(x, y, 40, 28, '#263238', 5) + circ(x + 20, y + 14, 9, '#90a4ae')
def mapp(x, y): return rect(x, y, 56, 40, '#fff3c4', 3, "stroke='#c9a227' stroke-width='2'") + line(x + 8, y + 10, x + 46, y + 30, '#2a9d8f', 3)
def flowers(x, y): return line(x, y, x, y + 40, '#2e7d32', 4) + circ(x, y, 10, '#f06292') + circ(x - 12, y + 8, 8, '#ba68c8') + circ(x + 12, y + 8, 8, '#ffb74d')
def paper(x, y): return rect(x, y, 34, 44, '#ffffff', 2, "stroke='#999' stroke-width='2'") + line(x + 6, y + 12, x + 28, y + 12, '#bbb', 2) + line(x + 6, y + 22, x + 28, y + 22, '#bbb', 2)
def pen(x, y): return line(x, y, x + 36, y - 6, '#1565c0', 5)
def clock(x, y): return circ(x, y, 22, '#ffffff', "stroke='#555' stroke-width='3'") + line(x, y, x, y - 14, '#333', 3) + line(x, y, x + 10, y + 6, '#333', 3)
def moon(x, y): return circ(x, y, 18, '#fff59d') + circ(x + 9, y - 6, 16, '#1a237e')
def sofa(x, w=220): return rect(x, 220, w, 70, '#8e7cc3', 18) + rect(x, 260, w, 40, '#7e6bb5', 10)
def mountain(): return rect(0, 0, W, H, '#cfe8ff') + path('M0,300 L170,120 L330,300 Z', '#90a4ae') + path('M120,175 L170,120 L220,175 Q170,160 120,175 Z', '#ffffff') + rect(0, 290, W, 42, '#a5d6a7') + rect(470, 150, 12, 150, '#c62828') + rect(560, 150, 12, 150, '#c62828') + rect(450, 150, 142, 14, '#c62828', 4) + rect(462, 175, 118, 10, '#c62828') + rect(0, G, W, H - G, '#8d9e74')

def scene(key):
    """returns svg body and speaker (x, top)"""
    S = []
    def P(*a, **k):
        s, top = person(*a, **k); S.append(s); return top
    if key == 'school_morning':
        S.append(room('#eef3e6')); S.append(board()); t = P(220, 'F', '#e76f51', s=0.9); P(440, 'M', '#455a64', kind='teacher'); S.append(bag(170, 230)); sp = (220, t)
    elif key == 'meal':
        S.append(room()); t = P(300, 'M', '#43aa8b', pose='palms', sit=True); P(470, 'F', '#f28482', sit=True); S.append(table(170, 400)); S.append(bowl(300, 258)); S.append(bowl(470, 258)); sp = (300, t)
    elif key == 'door_out':
        S.append(room()); S.append(door(470, out='#bfe3ff')); t = P(420, 'M', '#277da1', pose='wave', s=0.9); S.append(bag(370, 236)); P(200, 'F', '#f28482', pose='wave'); sp = (420, t)
    elif key == 'shop_fruit':
        S.append(room('#fff8e1', '#cfd8dc')); P(470, 'M', '#2a9d8f', kind='clerk'); S.append(rect(380, 230, 220, 102, '#bc8a5f', 6)); S.append(apples(410, 200)); t = P(220, 'F', '#9b5de5', pose='point'); sp = (220, t)
    elif key == 'gift':
        S.append(room('#fdf0f5')); P(420, 'F', '#f15bb5', pose='holdl', s=0.95); S.append(boxgift(330, 208)); t = P(220, 'M', '#00bbf9', s=0.95); sp = (220, t)
    elif key == 'train_foot':
        S.append(train()); P(420, 'M', '#6d597a', s=1); t = P(310, 'F', '#e56b6f', pose='palms', s=0.95); S.append(path('M372,322 l8,-14 l8,14 l14,-2 l-10,10 l6,14 l-14,-6 l-12,8 l2,-14 l-12,-8 Z', '#ffd166')); sp = (310, t)
    elif key == 'door_in':
        S.append(room()); S.append(door(470, out='#ffcc80')); t = P(440, 'F', '#f8961e', pose='wave', s=0.9); S.append(bag(480, 236)); P(200, 'F', '#90be6d'); sp = (440, t)
    elif key == 'office_door':
        S.append(room('#eceff1', '#b0bec5')); S.append(door(70, out='#cfd8dc')); t = P(220, 'M', '#4361ee', pose='point', s=0.9); P(470, 'M', '#455a64', kind='teacher', sit=True); S.append(desk(390, 200)); S.append(paper(420, 212)); sp = (220, t)
    elif key == 'night':
        S.append(room('#283593', '#5c6bc0')); S.append(window(60, 50, 150, 110, '#1a237e')); S.append(moon(110, 95)); S.append(bed(380, 240)); t = P(330, 'F', '', kind='pajama', s=0.85); P(200, 'M', '#795548'); sp = (330, t)
    elif key == 'pen':
        S.append(room('#eef3e6')); S.append(board(380, 40, 220, 90)); P(450, 'M', '#00a6a6', sit=True, s=0.9); S.append(desk(390, 150, 255)); S.append(pen(430, 252)); t = P(200, 'F', '#ef476f', pose='point', sit=True, s=0.9); S.append(desk(140, 140, 255)); sp = (200, t)
    elif key == 'hospital':
        S.append(room('#e8f5e9', '#cfd8dc')); S.append(bed(340, 260)); S.append(circ(380, 228, 22, SKIN)); S.append(path('M356,222 Q380,196 404,222 Z', '#2d2018')); S.append(rect(400, 222, 190, 24, '#a5d6a7', 8)); t = P(200, 'F', '#4895ef', pose='holdr'); S.append(flowers(258, 228)); sp = (200, t)
    elif key == 'hot_room':
        S.append(room('#fff3e0')); S.append(window(400, 50, 180, 130, '#bfe3ff')); S.append(sun(470, 100)); t = P(200, 'M', '#f3722c', pose='fan'); S.append(path('M238,108 q6,10 0,14 q-6,-4 0,-14 Z', '#4fc3f7')); P(470, 'F', '#577590'); sp = (200, t)
    elif key == 'rain':
        S.append(street('#b0bec5')); S.append(rain()); t = P(220, 'F', '#8338ec', pose='up', s=0.95); top2 = P(430, 'M', '#3a86ff', pose='holdl'); S.append(umbrella(430, top2)); sp = (220, t)
    elif key == 'boxes':
        S.append(room('#eceff1', '#bcaaa4')); P(430, 'F', '#5e548e', kind='teacher', pose='hold'); S.append(rect(392, 196, 76, 40, '#c8a06a', 4) + rect(396, 236, 68, 38, '#b88b4a', 4)); t = P(220, 'M', '#2a9d8f', s=0.9); sp = (220, t)
    elif key == 'late':
        S.append(room('#eef3e6')); S.append(board(300, 40, 260, 110)); S.append(door(40, out='#cfd8dc')); t = P(160, 'M', '#e76f51', pose='palms', s=0.9); P(470, 'F', '#264653', kind='teacher', pose='pointl'); sp = (160, t)
    elif key == 'restaurant':
        S.append(room('#fff8e1', '#a1887f')); t = P(200, 'F', '#06d6a0', pose='wave', sit=True); S.append(table(100, 230)); S.append(rect(250, 228, 22, 34, '#e3f2fd', 3, "stroke='#90caf9' stroke-width='2'")); P(450, 'M', '#212121', kind='clerk'); sp = (200, t)
    elif key == 'photo':
        S.append(mountain()); t = P(220, 'M', '#118ab2', pose='holdr'); S.append(cam(258, 120)); P(400, 'F', '#ef476f'); sp = (220, t)
    elif key == 'office_leave':
        S.append(room('#eceff1', '#90a4ae')); S.append(desk(360, 240)); S.append(monitor(400, 194)); S.append(monitor(510, 194)); P(450, 'F', '#577590', sit=True); t = P(200, 'M', '#2b2d42', pose='wave'); S.append(bag(140, 236)); sp = (200, t)
    elif key == 'visit':
        S.append(street('#cfe8ff')); S.append(door(420, 140, out='#f6efe3')); P(490, 'F', '#f28482', pose='wave', s=0.9); t = P(300, 'M', '#43aa8b', pose='hold', s=0.9); S.append(boxgift(284, 206, 30)); sp = (300, t)
    elif key == 'lost':
        S.append(street()); t = P(220, 'F', '#ff9f1c', pose='holdr'); S.append(mapp(258, 150)); P(430, 'M', '#2ec4b6'); sp = (220, t)
    elif key == 'leave_friend':
        S.append(room('#f3e9f7')); S.append(clock(560, 60)); S.append(window(40, 50, 140, 100, '#ffb74d')); S.append(sofa(360)); P(450, 'F', '#f28482', sit=True); t = P(220, 'F', '#4cc9f0', pose='holdr', s=0.95); S.append(bag(258, 228)); sp = (220, t)
    elif key == 'teacher_doc':
        S.append(room('#eceff1', '#b0bec5')); P(460, 'M', '#455a64', kind='teacher', sit=True); S.append(desk(380, 210)); t = P(230, 'M', '#3a0ca3', pose='holdr', s=0.9); S.append(paper(275, 160)); sp = (230, t)
    elif key == 'seat':
        S.append(train()); S.append(bench(120, 260)); t = P(240, 'F', '#2a9d8f', sit=True); P(460, 'M', '#8d6e63', kind='old'); sp = (240, t)
    else:
        raise KeyError(key)
    S.append(arrow(*sp))
    return ''.join(S)

def svg(key):
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img'>{scene(key)}</svg>"

if __name__ == '__main__':
    import sys, os
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for k in sys.argv[2:]: open(f'{out}/{k}.svg', 'w').write(svg(k))
