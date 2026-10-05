#!/usr/bin/env python3
"""Generates the animated deep-space / scanner SVG assets for the profile README.

Palette is sampled from a Milky Way night-sky photo: near-black navy sky,
dusty beige / rose galactic core, muted teal haze and blue-white starlight.

Run:  python scripts/generate_assets.py   (writes into ./assets)
"""
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "assets"))
os.makedirs(OUT, exist_ok=True)

FONT = "'JetBrains Mono','Fira Code','Cascadia Code',Consolas,'Courier New',monospace"

# ---- palette (from the photo) ------------------------------------------------
SKY0 = "#020409"   # zenith
SKY1 = "#060a14"
SKY2 = "#0f1727"   # near horizon
BEIGE = "#d6c5a5"  # galactic core dust
ROSE = "#bb8c82"   # reddish nebula
TEAL = "#86ad9f"   # greenish haze
SCAN = "#a9e2d4"   # scanner accent (pale teal light)
STAR = "#f4f7ff"
BLUE = "#c4d8ff"   # blue-white star glow
TEXT = "#e6e9ef"
MUTED = "#7d869a"
DIM = "#3a4358"
LINE = "#1b2336"
PANEL = "#070b14"


def save(name, body, w, h):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none" xml:space="preserve">\n{body}\n</svg>\n'
    )
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote assets/{name}  ({len(svg) // 1024} KB)")


def base_css(extra=""):
    return f"""<style>
text{{font-family:{FONT};white-space:pre;}}
.tw{{animation:tw 4s ease-in-out infinite;}}
@keyframes tw{{0%,100%{{opacity:.12}}50%{{opacity:1}}}}
.blink{{animation:blink 1.1s steps(1) infinite;}}
@keyframes blink{{50%{{opacity:0}}}}
{extra}
</style>"""


def common_defs(h):
    return f"""
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{SKY0}"/><stop offset=".6" stop-color="{SKY1}"/><stop offset="1" stop-color="{SKY2}"/>
</linearGradient>
<radialGradient id="mwBase"><stop offset="0" stop-color="{BEIGE}" stop-opacity=".45"/><stop offset=".5" stop-color="{ROSE}" stop-opacity=".12"/><stop offset="1" stop-color="{SKY0}" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{SCAN}" stop-opacity="0"/><stop offset=".85" stop-color="{SCAN}" stop-opacity=".07"/><stop offset=".985" stop-color="{SCAN}" stop-opacity=".35"/><stop offset="1" stop-color="{SCAN}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="hglow" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{TEAL}" stop-opacity="0"/><stop offset=".7" stop-color="{TEAL}" stop-opacity=".07"/><stop offset="1" stop-color="{BEIGE}" stop-opacity=".16"/>
</linearGradient>
<pattern id="scanlines" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>
<filter id="blurL" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="38"/></filter>
<filter id="blurM" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="15"/></filter>
<filter id="blurS" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
"""


def starfield(w, h, n, tw=0.2, seed=1, y0=0):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(y0, h)
        r = 0.3 + rnd.random() ** 4 * 1.6
        col = rnd.choice([STAR] * 7 + [BLUE, BLUE, BEIGE])
        if rnd.random() < tw:
            d, dl = rnd.uniform(2.5, 6.5), -rnd.uniform(0, 6)
            out.append(f'<circle class="tw" cx="{x:.1f}" cy="{y:.1f}" r="{r + .2:.2f}" fill="{col}" '
                       f'style="animation-duration:{d:.1f}s;animation-delay:{dl:.1f}s"/>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{col}" opacity="{rnd.uniform(.25, .9):.2f}"/>')
    return "\n".join(out)


def milky_way(cx, cy, length, angle, scale=1.0, seed=3):
    rnd = random.Random(seed)
    g = [f'<g transform="rotate({angle} {cx} {cy})">',
         f'<ellipse cx="{cx}" cy="{cy}" rx="{length / 2:.0f}" ry="{75 * scale:.0f}" fill="url(#mwBase)" filter="url(#blurL)"/>']
    for _ in range(int(40 * scale) + 10):
        t = max(-1, min(1, rnd.gauss(0, .35)))
        x, y = cx + t * length / 2, cy + rnd.gauss(0, 22 * scale)
        core = abs(t) < .4
        col = rnd.choices([BEIGE, ROSE, TEAL], weights=[5 if core else 2, 2, 1 if core else 3])[0]
        op = rnd.uniform(.06, .2) * (1 - abs(t) * .6)
        g.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rnd.uniform(40, 140) * scale:.0f}" '
                 f'ry="{rnd.uniform(14, 45) * scale:.0f}" fill="{col}" opacity="{op:.2f}" filter="url(#blurM)"/>')
    for _ in range(int(10 * scale) + 4):  # dark dust lanes
        t = rnd.uniform(-.7, .7)
        g.append(f'<ellipse cx="{cx + t * length / 2:.0f}" cy="{cy + rnd.gauss(0, 8 * scale):.0f}" '
                 f'rx="{rnd.uniform(40, 120) * scale:.0f}" ry="{rnd.uniform(4, 10) * scale:.0f}" '
                 f'fill="{SKY0}" opacity="{rnd.uniform(.25, .5):.2f}" filter="url(#blurS)"/>')
    for _ in range(int(650 * scale)):  # dense star clouds
        t = rnd.gauss(0, .4)
        g.append(f'<circle cx="{cx + t * length / 2:.1f}" cy="{cy + rnd.gauss(0, 30 * scale):.1f}" '
                 f'r="{.25 + rnd.random() ** 5 * 1.1:.2f}" fill="{rnd.choice([STAR, STAR, BEIGE, BLUE])}" '
                 f'opacity="{rnd.uniform(.25, .85):.2f}"/>')
    g.append("</g>")
    return "\n".join(g)


def bright_star_defs():
    return f"""
<radialGradient id="starGlow"><stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset=".1" stop-color="{BLUE}" stop-opacity=".45"/><stop offset=".4" stop-color="{BLUE}" stop-opacity=".1"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<linearGradient id="spike" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>
"""


def bright_star(x, y, s=1.0, lock=True):
    lock_svg = ""
    if lock:
        h = 26
        lock_svg = f"""
<g class="lock" stroke="{SCAN}" stroke-width="1.5" fill="none">
  <path d="M-{h},-{h - 10} V-{h} H-{h - 10} M{h - 10},-{h} H{h} V-{h - 10} M{h},{h - 10} V{h} H{h - 10} M-{h - 10},{h} H-{h} V{h - 10}"/>
</g>
<g class="lockLabel">
  <path d="M{h},-{h} L{h + 26},-{h + 22} H{h + 140}" stroke="{SCAN}" stroke-opacity=".6" stroke-width="1"/>
  <text x="{h + 30}" y="-{h + 28}" font-size="11" fill="{SCAN}" letter-spacing="1">OBJ-01 · LOCKED</text>
  <text x="{h + 30}" y="-{h + 8}" font-size="10" fill="{MUTED}">MAG -1.46 · Δ 0.003″</text>
</g>"""
    return f"""<g transform="translate({x} {y})">
<g class="flare">
  <circle r="{48 * s}" fill="url(#starGlow)"/>
  <g transform="rotate(-38)">
    <polygon points="-{100 * s},0 0,-1.4 {100 * s},0 0,1.4" fill="url(#spike)"/>
    <polygon points="0,-{42 * s} 1.1,0 0,{42 * s} -1.1,0" fill="{BLUE}" opacity=".55"/>
  </g>
  <g transform="rotate(8)">
    <polygon points="-{30 * s},0 0,-.8 {30 * s},0 0,.8" fill="{STAR}" opacity=".5"/>
    <polygon points="0,-{24 * s} .8,0 0,{24 * s} -.8,0" fill="{STAR}" opacity=".45"/>
  </g>
  <circle r="{3.2 * s}" fill="#fff"/>
</g>{lock_svg}
</g>"""


def silhouette(x, ground):
    """Tiny human figure standing on the horizon (nod to the photo)."""
    b = ground
    return (f'<g fill="#000"><circle cx="{x}" cy="{b - 32}" r="4.4"/>'
            f'<path d="M{x - 6.5},{b - 26} Q{x},{b - 28.5} {x + 6.5},{b - 26} L{x + 8},{b - 10} L{x + 4.5},{b - 10} '
            f'L{x + 3.5},{b + 1} L{x - 3.5},{b + 1} L{x - 4.5},{b - 10} L{x - 8},{b - 10} Z"/></g>')


def corner_brackets(x, y, w, h, size=16, color=SCAN, op=.7):
    s = size
    return (f'<path d="M{x},{y + s} V{y} H{x + s} M{x + w - s},{y} H{x + w} V{y + s} '
            f'M{x + w},{y + h - s} V{y + h} H{x + w - s} M{x + s},{y + h} H{x} V{y + h - s}" '
            f'stroke="{color}" stroke-opacity="{op}" stroke-width="1.5" fill="none"/>')


# =============================================================================
# 1) HEADER
# =============================================================================
def header():
    W, H, GROUND = 1200, 420, 372
    css = f"""
.flare{{transform-origin:0 0;animation:pulse 4s ease-in-out infinite;}}
@keyframes pulse{{0%,100%{{transform:scale(.92);opacity:.85}}50%{{transform:scale(1.08);opacity:1}}}}
.lock{{transform-origin:0 0;animation:lock 6s ease-out infinite;}}
@keyframes lock{{0%{{transform:scale(2.2) rotate(45deg);opacity:0}}12%{{transform:scale(1) rotate(0);opacity:1}}80%{{opacity:1}}86%{{opacity:.2}}90%{{opacity:1}}100%{{opacity:0}}}}
.lockLabel{{animation:lbl 6s steps(1) infinite;}}
@keyframes lbl{{0%,12%{{opacity:0}}14%,86%{{opacity:1}}88%{{opacity:0}}90%,100%{{opacity:1}}}}
.beam{{animation:beam 6s linear infinite;}}
@keyframes beam{{0%{{transform:translateY(-110px)}}100%{{transform:translateY({H}px)}}}}
.shoot{{animation:shoot 11s ease-in infinite;}}
@keyframes shoot{{0%{{transform:translate(0,0);opacity:0}}2%{{opacity:1}}8%{{transform:translate(-340px,170px);opacity:0}}100%{{opacity:0;transform:translate(-340px,170px)}}}}
.title{{animation:flick 7s infinite;}}
@keyframes flick{{0%,88%,100%{{opacity:1}}89%{{opacity:.55}}90%{{opacity:1}}94%{{opacity:.7}}95%{{opacity:1}}}}
.g1,.g2{{opacity:0;animation:g1 7s steps(1) infinite;}}
.g2{{animation-name:g2;}}
@keyframes g1{{0%,88%{{opacity:0;transform:none}}89%{{opacity:.8;transform:translate(-6px,1px)}}90%{{opacity:.5;transform:translate(3px,-2px)}}91%,93%{{opacity:0}}94%{{opacity:.7;transform:translate(-3px,0)}}95%,100%{{opacity:0}}}}
@keyframes g2{{0%,88%{{opacity:0;transform:none}}89%{{opacity:.8;transform:translate(6px,-1px)}}90%{{opacity:.5;transform:translate(-4px,2px)}}91%,93%{{opacity:0}}94%{{opacity:.7;transform:translate(4px,1px)}}95%,100%{{opacity:0}}}}
"""
    tx, ty = 609, 205
    title = "AVENOIR"
    sub = "CYBERSECURITY ENGINEER"
    body = f"""{base_css(css)}
<defs>{common_defs(H)}{bright_star_defs()}
<linearGradient id="shootG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="typeClip"><rect x="355" y="228" height="34" width="0"><animate attributeName="width" from="0" to="490" begin=".8s" dur="2.4s" fill="freeze"/></rect></clipPath>
</defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{milky_way(640, 215, 1500, -24, 1.0, seed=11)}
{starfield(W, GROUND, 380, tw=.22, seed=5)}
<rect y="{GROUND - 90}" width="{W}" height="90" fill="url(#hglow)"/>
<g class="shoot"><line x1="1050" y1="40" x2="1130" y2="0" stroke="url(#shootG)" stroke-width="1.6"/></g>
{bright_star(935, 96)}
<rect y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#010204"/>
<line x1="0" y1="{GROUND}" x2="{W}" y2="{GROUND}" stroke="{BEIGE}" stroke-opacity=".12"/>
{silhouette(270, GROUND)}
<rect width="{W}" height="{H}" fill="url(#scanlines)" opacity=".35"/>
<rect class="beam" width="{W}" height="110" fill="url(#beam)"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>

<!-- HUD -->
{corner_brackets(16, 16, W - 32, H - 32, 22, SCAN, .55)}
<text x="44" y="46" font-size="12" fill="{MUTED}" letter-spacing="2">SYS://AVENOIR.DEEP-SPACE</text>
<text x="44" y="64" font-size="11" fill="{SCAN}" letter-spacing="1"><tspan class="blink">●</tspan> UPLINK ESTABLISHED</text>
<text x="{W - 44}" y="46" font-size="11" fill="{MUTED}" text-anchor="end" letter-spacing="1">RA 17h45m40s · DEC −29°00′28″</text>
<text x="44" y="{H - 30}" font-size="11" fill="{MUTED}" letter-spacing="1">SCAN MODE: PASSIVE · SECTOR 0x7E3</text>
<text x="{W - 44}" y="{H - 30}" font-size="11" fill="{MUTED}" text-anchor="end" letter-spacing="1">SIGNAL <tspan fill="{SCAN}">▮▮▮▮▮▮</tspan><tspan fill="{DIM}">▮▮</tspan> 78%</text>

<!-- TITLE -->
<g font-size="92" font-weight="700" letter-spacing="18" text-anchor="middle">
  <text class="g1" x="{tx}" y="{ty}" fill="{TEAL}">{title}</text>
  <text class="g2" x="{tx}" y="{ty}" fill="{ROSE}">{title}</text>
  <text class="title" x="{tx}" y="{ty}" fill="{TEXT}" filter="url(#glow)">{title}</text>
</g>
<line x1="420" y1="226" x2="780" y2="226" stroke="{BEIGE}" stroke-opacity=".35"/>
<g clip-path="url(#typeClip)">
  <text x="{tx - 4}" y="254" font-size="20" fill="{BEIGE}" letter-spacing="8" text-anchor="middle">{sub}</text>
</g>
<text x="600" y="292" font-size="12" fill="{MUTED}" letter-spacing="3" text-anchor="middle">// SECURITY IS NOT A FEATURE. IT'S A MINDSET.</text>
"""
    save("header.svg", body, W, H)


# =============================================================================
# 2) DIVIDER
# =============================================================================
def divider():
    W, H = 1200, 24
    css = """.mv{animation:mv 5s linear infinite;}
@keyframes mv{0%{transform:translateX(-260px)}100%{transform:translateX(1200px)}}"""
    body = f"""{base_css(css)}
<defs><linearGradient id="dg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{SCAN}" stop-opacity="0"/><stop offset=".85" stop-color="{SCAN}" stop-opacity=".9"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>
<line x1="20" y1="12" x2="{W - 20}" y2="12" stroke="{LINE}" stroke-width="1.5"/>
<rect class="mv" x="0" y="11" width="260" height="2" fill="url(#dg)"/>
<path d="M8,12 l6,-5 l6,5 l-6,5z M{W - 20},12 l6,-5 l6,5 l-6,5z" fill="{BEIGE}" opacity=".6"/>
"""
    save("divider.svg", body, W, H)


# =============================================================================
# 3) WHOAMI TERMINAL + BIOMETRIC SCAN
# =============================================================================
def whoami():
    W, H = 1200, 420
    rnd = random.Random(21)
    css = f""".beam{{animation:beam 5s linear infinite;}}
@keyframes beam{{0%{{transform:translateY(-110px)}}100%{{transform:translateY({H}px)}}}}
.grant{{animation:grant 2.4s steps(1) infinite;}}
@keyframes grant{{0%,70%{{opacity:1}}71%,85%{{opacity:.25}}86%{{opacity:1}}}}"""

    def kv(k, v, vcol=TEXT):
        dots = "." * (14 - len(k))
        return (f'<tspan fill="{BEIGE}">{k}</tspan> <tspan fill="{DIM}">{dots}</tspan> '
                f'<tspan fill="{vcol}">{v}</tspan>')

    lines = [
        f'<tspan fill="{SCAN}">$</tspan> <tspan fill="{TEXT}">./scan_identity --target=self --deep</tspan>',
        f'<tspan fill="{MUTED}">[*] initializing biometric scanner ... done</tspan>',
        kv("name", "Avenoir"),
        kv("role", "Cybersecurity Engineer"),
        kv("focus", "Security • Software • Development"),
        kv("languages", "Python • C++ • Dart • HTML • CSS"),
        kv("framework", "Flutter"),
        kv("environment", "Linux • Git • GitHub"),
        kv("status", "● ONLINE — transmitting from deep space", SCAN),
    ]
    clips, texts = [], []
    for i, ln in enumerate(lines):
        y = 86 + i * 33
        begin = .4 + i * .5
        clips.append(f'<clipPath id="l{i}"><rect x="30" y="{y - 22}" height="32" width="0">'
                     f'<animate attributeName="width" from="0" to="790" begin="{begin:.2f}s" dur=".55s" fill="freeze"/></rect></clipPath>')
        texts.append(f'<text x="40" y="{y}" font-size="16" clip-path="url(#l{i})">{ln}</text>')
    last_y = 86 + len(lines) * 33

    # fingerprint ridges
    fx, fy = 1005, 222
    ridges = []
    for k in range(12):
        rx, ry = 5 + k * 7.5, 8 + k * 9
        segs = " ".join(str(rnd.randint(8, 60)) if j % 2 == 0 else str(rnd.randint(3, 9)) for j in range(6))
        ridges.append((rx, ry, segs, rnd.randint(0, 80)))

    def ridge_group(color, op):
        return "\n".join(
            f'<ellipse cx="{fx}" cy="{fy}" rx="{rx}" ry="{ry}" stroke="{color}" stroke-opacity="{op}" stroke-width="2.3" '
            f'stroke-linecap="round" stroke-dasharray="{segs}" stroke-dashoffset="{off}"/>' for rx, ry, segs, off in ridges)

    body = f"""{base_css(css)}
<defs>{common_defs(H)}
{''.join(clips)}
<clipPath id="fp"><ellipse cx="{fx}" cy="{fy}" rx="80" ry="100"/></clipPath>
<clipPath id="band"><rect x="900" y="110" width="210" height="34"><animate attributeName="y" values="108;300;108" dur="3.4s" repeatCount="indefinite"/></rect></clipPath>
<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SCAN}" stop-opacity="0"/><stop offset="1" stop-color="{SCAN}" stop-opacity=".35"/></linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>
<g opacity=".7">{starfield(W, H, 90, tw=.3, seed=8, y0=44)}</g>
<path d="M1,42 H{W - 1}" stroke="{LINE}" stroke-width="1.5"/>
<circle cx="26" cy="22" r="6" fill="{ROSE}"/><circle cx="46" cy="22" r="6" fill="{BEIGE}"/><circle cx="66" cy="22" r="6" fill="{TEAL}"/>
<text x="600" y="27" font-size="13" fill="{MUTED}" text-anchor="middle">avenoir@deep-space: ~/identity</text>
{''.join(texts)}
<text x="40" y="{last_y}" font-size="16"><tspan fill="{SCAN}">$</tspan> <tspan class="blink" fill="{SCAN}">▋</tspan></text>

<!-- biometric panel -->
<rect x="852" y="62" width="306" height="336" rx="8" fill="#0a111c" fill-opacity=".85" stroke="{LINE}"/>
{corner_brackets(852, 62, 306, 336, 18, SCAN, .8)}
<text x="872" y="90" font-size="12" fill="{SCAN}" letter-spacing="2">BIOMETRIC SCAN</text>
<text x="1138" y="90" font-size="11" fill="{MUTED}" text-anchor="end"><tspan class="blink">●</tspan> REC</text>
<g clip-path="url(#fp)">
  {ridge_group(TEAL, .28)}
  <g clip-path="url(#band)">{ridge_group(SCAN, 1)}</g>
</g>
<g>
  <rect x="905" y="108" width="200" height="34" fill="url(#sg)"><animate attributeName="y" values="108;300;108" dur="3.4s" repeatCount="indefinite"/></rect>
  <rect x="905" y="141" width="200" height="1.5" fill="{SCAN}"><animate attributeName="y" values="141;333;141" dur="3.4s" repeatCount="indefinite"/></rect>
</g>
<text x="872" y="354" font-size="11" fill="{MUTED}">SUBJECT <tspan fill="{TEXT}">AVENOIR</tspan>   MATCH <tspan fill="{BEIGE}">99.97%</tspan></text>
<text class="grant" x="1005" y="380" font-size="13" fill="{SCAN}" text-anchor="middle" letter-spacing="3">ACCESS GRANTED</text>
<rect class="beam" x="1" width="{W - 2}" height="110" fill="url(#beam)" opacity=".7"/>
"""
    save("whoami.svg", body, W, H)


# =============================================================================
# 4) RADAR / THREAT SCANNER
# =============================================================================
def radar():
    W, H = 1200, 380
    cx, cy, R = 195, 190, 150
    T = 4.0      # sweep period
    C = 12.0     # log cycle
    rnd = random.Random(42)

    rows = [
        ("OK", "perimeter.firewall", "ACTIVE"),
        ("OK", "ids.intrusion_detect", "ARMED"),
        ("OK", "crypto.channel", "AES-256-GCM"),
        ("OK", "ports.scan 22/80/443", "FILTERED"),
        ("!!", "anomalies.detected", "0"),
        ("OK", "integrity.checksum", "PASSED"),
    ]
    kf = []
    for i in range(len(rows)):
        p = (.6 + i * .65) / C * 100
        kf.append(f"@keyframes r{i}{{0%,{p:.1f}%{{opacity:0;transform:translateX(-8px)}}"
                  f"{p + 2:.1f}%,93%{{opacity:1;transform:translateX(0)}}100%{{opacity:0}}}}"
                  f".r{i}{{animation:r{i} {C}s linear infinite;}}")
    pct_p = (.6 + len(rows) * .65 + 2.2) / C * 100
    css = f""".sweep{{transform-origin:{cx}px {cy}px;animation:spin {T}s linear infinite;}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.blip{{opacity:0;animation:blip {T}s linear infinite;}}
@keyframes blip{{0%{{opacity:1}}70%{{opacity:.1}}100%{{opacity:0}}}}
.hex{{animation:hex 18s linear infinite;}}
@keyframes hex{{to{{transform:translateY(-320px)}}}}
.pct{{animation:pct {C}s steps(1) infinite;}}
@keyframes pct{{0%,{pct_p:.1f}%{{opacity:0}}{pct_p + .1:.1f}%,93%{{opacity:1}}100%{{opacity:0}}}}
{''.join(kf)}"""

    def pt(a, r):
        a = math.radians(a)
        return cx + r * math.cos(a), cy + r * math.sin(a)

    parts = []
    # rings, crosshair, ticks
    for f in (.25, .5, .75):
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R * f}" stroke="{TEAL}" stroke-opacity=".22" stroke-dasharray="2 4"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" stroke="{TEAL}" stroke-opacity=".6" stroke-width="1.5"/>')
    parts.append(f'<path d="M{cx - R},{cy} H{cx + R} M{cx},{cy - R} V{cy + R}" stroke="{TEAL}" stroke-opacity=".2"/>')
    for a in range(0, 360, 5):
        ln = 12 if a % 30 == 0 else 5
        x1, y1 = pt(a, R)
        x2, y2 = pt(a, R - ln)
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{TEAL}" stroke-opacity=".55"/>')
    for a, lbl in ((270, "000"), (0, "090"), (90, "180"), (180, "270")):
        x, y = pt(a, R + 15)
        parts.append(f'<text x="{x:.0f}" y="{y + 4:.0f}" font-size="10" fill="{MUTED}" text-anchor="middle">{lbl}</text>')

    # sweep trail wedges
    wedges = []
    n = 45
    for i in range(n):
        a1, a0 = -i * 1.4, -(i + 1) * 1.4
        x1, y1 = pt(a1, R)
        x0, y0 = pt(a0, R)
        op = .42 * (1 - i / n) ** 1.7
        wedges.append(f'<path d="M{cx},{cy} L{x1:.2f},{y1:.2f} A{R},{R} 0 0 0 {x0:.2f},{y0:.2f} Z" fill="{SCAN}" opacity="{op:.3f}"/>')
    ex, ey = pt(0, R)
    wedges.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{SCAN}" stroke-width="2"/>')

    blips = []
    for j in range(8):
        a = rnd.uniform(0, 360)
        r = rnd.uniform(.2, .88) * R
        x, y = pt(a, r)
        col = BEIGE if j in (2, 5) else SCAN
        d = a / 360 * T
        blips.append(f'<g class="blip" style="animation-delay:{d:.2f}s"><circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{col}"/>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" stroke="{col}" stroke-opacity=".5"/></g>')
        if j in (2, 5):
            blips.append(f'<g class="blip" style="animation-delay:{d:.2f}s"><text x="{x + 11:.0f}" y="{y - 8:.0f}" font-size="9" fill="{BEIGE}">0x{rnd.randint(16, 255):02X}</text></g>')

    # log rows
    row_svg = []
    for i, (tag, key, val) in enumerate(rows):
        y = 112 + i * 32
        tcol = SCAN if tag == "OK" else BEIGE
        dots = "." * (24 - len(key))
        row_svg.append(f'<text class="r{i}" x="400" y="{y}" font-size="14">'
                       f'<tspan fill="{DIM}">[</tspan><tspan fill="{tcol}">{tag}</tspan><tspan fill="{DIM}">]</tspan> '
                       f'<tspan fill="{TEXT}">{key}</tspan> <tspan fill="{DIM}">{dots}</tspan> <tspan fill="{tcol}">{val}</tspan></text>')

    # hex stream (duplicated for seamless loop)
    hex_lines = []
    for k in range(20):
        addr = 0x0F00 + k * 16
        bs = [f"{rnd.randint(0, 255):02X}" for _ in range(8)]
        hi = rnd.randint(0, 7) if rnd.random() < .35 else -1
        spans = " ".join(f'<tspan fill="{SCAN}">{b}</tspan>' if idx == hi else b for idx, b in enumerate(bs))
        hex_lines.append((addr, spans))
    hex_svg = []
    for rep in range(2):
        for k, (addr, spans) in enumerate(hex_lines):
            y = 96 + rep * 320 + k * 16
            hex_svg.append(f'<text x="968" y="{y}" font-size="11" fill="{DIM}"><tspan fill="{MUTED}">0x{addr:04X}</tspan>  {spans}</text>')

    body = f"""{base_css(css)}
<defs>{common_defs(H)}
<radialGradient id="rbg"><stop offset="0" stop-color="#0e1b1d"/><stop offset="1" stop-color="#05080d"/></radialGradient>
<clipPath id="rc"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>
<clipPath id="hc"><rect x="960" y="78" width="215" height="282"/></clipPath>
<linearGradient id="pg" x1="400" y1="0" x2="930" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{TEAL}"/><stop offset=".6" stop-color="{BEIGE}"/><stop offset="1" stop-color="{ROSE}"/></linearGradient>
<linearGradient id="hfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PANEL}"/><stop offset=".15" stop-color="{PANEL}" stop-opacity="0"/><stop offset=".85" stop-color="{PANEL}" stop-opacity="0"/><stop offset="1" stop-color="{PANEL}"/></linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>
<g opacity=".6">{starfield(W, H, 110, tw=.3, seed=9)}</g>
<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#rbg)"/>
{''.join(parts)}
<g clip-path="url(#rc)"><g class="sweep">{''.join(wedges)}</g></g>
{''.join(blips)}
<circle cx="{cx}" cy="{cy}" r="3" fill="{SCAN}"/>

<text x="400" y="60" font-size="18" font-weight="700" fill="{TEXT}" letter-spacing="2">THREAT_SCANNER <tspan font-weight="400" fill="{MUTED}" font-size="13">v2.6 · deep-space node</tspan></text>
<text x="930" y="60" font-size="12" fill="{ROSE}" text-anchor="end" letter-spacing="2"><tspan class="blink">●</tspan> LIVE</text>
<line x1="400" y1="76" x2="930" y2="76" stroke="{LINE}" stroke-width="1.5"/>
{''.join(row_svg)}
<text x="400" y="318" font-size="11" fill="{MUTED}" letter-spacing="2">SYSTEM INTEGRITY</text>
<text class="pct" x="930" y="318" font-size="11" fill="{SCAN}" text-anchor="end" letter-spacing="1">100% SECURE</text>
<rect x="400" y="328" width="530" height="6" rx="3" fill="{LINE}"/>
<rect x="400" y="328" height="6" rx="3" width="0" fill="url(#pg)"><animate attributeName="width" values="0;0;530;530;0" keyTimes="0;.33;.6;.95;1" dur="{C}s" repeatCount="indefinite"/></rect>

<text x="968" y="60" font-size="12" fill="{MUTED}" letter-spacing="2">MEM_DUMP</text>
<line x1="960" y1="76" x2="1175" y2="76" stroke="{LINE}" stroke-width="1.5"/>
<g clip-path="url(#hc)"><g class="hex">{''.join(hex_svg)}</g></g>
<rect x="960" y="78" width="215" height="282" fill="url(#hfade)"/>
"""
    save("radar.svg", body, W, H)


# =============================================================================
# 5) SKILL MATRIX
# =============================================================================
def skills():
    W, H = 1200, 320
    X0, BW = 250, 830
    data = [("Security", .95), ("Python", .90), ("C++", .85), ("Flutter", .80), ("Web Development", .75)]
    css = f""".sh{{animation:sh 3.2s ease-in-out infinite;}}
@keyframes sh{{0%{{transform:translateX(-160px)}}100%{{transform:translateX({BW + 160}px)}}}}"""
    clips, bars = [], []
    for i, (name, v) in enumerate(data):
        y = 88 + i * 40
        end = v * BW
        begin = .3 + i * .18
        anim = (f'<animate attributeName="width" from="0" to="{end:.0f}" begin="{begin:.2f}s" dur="1.6s" fill="freeze" '
                f'calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>')
        clips.append(f'<clipPath id="b{i}"><rect x="{X0}" y="{y}" height="10" width="0" rx="2">{anim}</rect></clipPath>')
        bars.append(f"""
<text x="36" y="{y + 10}" font-size="15" fill="{TEXT}">{name}</text>
<rect x="{X0}" y="{y}" width="{BW}" height="10" rx="2" fill="{LINE}"/>
<rect x="{X0}" y="{y}" height="10" width="0" rx="2" fill="url(#bg)">{anim}</rect>
<g clip-path="url(#b{i})"><rect class="sh" x="{X0}" y="{y}" width="140" height="10" fill="url(#shine)" style="animation-delay:{i * .35:.2f}s"/></g>
<rect x="{X0}" y="{y - 4}" width="2" height="18" fill="{STAR}"><animate attributeName="x" from="{X0}" to="{X0 + end:.0f}" begin="{begin:.2f}s" dur="1.6s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/></rect>
<text x="{W - 36}" y="{y + 10}" font-size="14" fill="{SCAN}" text-anchor="end">{int(v * 100)}%</text>""")
    grid = []
    for j in range(11):
        x = X0 + j * BW / 10
        grid.append(f'<line x1="{x:.0f}" y1="76" x2="{x:.0f}" y2="270" stroke="{LINE}" stroke-dasharray="2 4"/>')
        grid.append(f'<text x="{x:.0f}" y="290" font-size="10" fill="{DIM}" text-anchor="middle">{j * 10}</text>')
    body = f"""{base_css(css)}
<defs>{common_defs(H)}{''.join(clips)}
<linearGradient id="bg" x1="{X0}" y1="0" x2="{X0 + BW}" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{TEAL}"/><stop offset=".55" stop-color="{BEIGE}"/><stop offset="1" stop-color="{ROSE}"/></linearGradient>
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".65"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>
<g opacity=".55">{starfield(W, H, 80, tw=.3, seed=13)}</g>
<text x="36" y="46" font-size="15" fill="{BEIGE}"><tspan fill="{SCAN}">&gt;</tspan> skill_matrix --scan --calibrated</text>
<text x="{W - 36}" y="46" font-size="11" fill="{MUTED}" text-anchor="end" letter-spacing="2"><tspan class="blink" fill="{SCAN}">●</tspan> ANALYZING</text>
{''.join(grid)}
{''.join(bars)}
"""
    save("skills.svg", body, W, H)


# =============================================================================
# 6) FOOTER
# =============================================================================
def footer():
    W, H, GROUND = 1200, 300, 232
    css = f""".beam{{animation:beam 7s linear infinite;}}
@keyframes beam{{0%{{transform:translateY(-110px)}}100%{{transform:translateY({H}px)}}}}"""
    code = (f'<tspan fill="{ROSE}">while</tspan><tspan fill="{BEIGE}"> (</tspan><tspan fill="{TEXT}">alive</tspan>'
            f'<tspan fill="{BEIGE}">) {{ </tspan>'
            f'<tspan fill="{SCAN}">learn</tspan><tspan fill="{TEXT}">(); </tspan>'
            f'<tspan fill="{SCAN}">build</tspan><tspan fill="{TEXT}">(); </tspan>'
            f'<tspan fill="{SCAN}">secure</tspan><tspan fill="{TEXT}">(); </tspan>'
            f'<tspan fill="{BEIGE}">}}</tspan><tspan class="blink" fill="{SCAN}"> ▋</tspan>')
    body = f"""{base_css(css)}
<defs>{common_defs(H)}{bright_star_defs()}
<style>.flare{{transform-origin:0 0;animation:pulse 4s ease-in-out infinite;}}@keyframes pulse{{0%,100%{{transform:scale(.9);opacity:.8}}50%{{transform:scale(1.05);opacity:1}}}}</style>
</defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{milky_way(600, 120, 1400, 12, .6, seed=17)}
{starfield(W, GROUND, 240, tw=.25, seed=19)}
{bright_star(170, 60, .6, lock=False)}
<rect y="{GROUND - 70}" width="{W}" height="70" fill="url(#hglow)"/>
<rect y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#010204"/>
<line x1="0" y1="{GROUND}" x2="{W}" y2="{GROUND}" stroke="{BEIGE}" stroke-opacity=".12"/>
{silhouette(930, GROUND)}
<rect width="{W}" height="{H}" fill="url(#scanlines)" opacity=".3"/>
<rect class="beam" width="{W}" height="110" fill="url(#beam)"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<text x="600" y="112" font-size="24" text-anchor="middle">{code}</text>
<text x="600" y="152" font-size="12" fill="{MUTED}" text-anchor="middle" letter-spacing="2">LEARN HOW IT WORKS · UNDERSTAND HOW IT BREAKS · BUILD IT BETTER · SECURE IT</text>
<text x="40" y="272" font-size="11" fill="{MUTED}" letter-spacing="2"><tspan class="blink" fill="{ROSE}">●</tspan> END OF TRANSMISSION</text>
<text x="{W - 40}" y="272" font-size="11" fill="{MUTED}" text-anchor="end" letter-spacing="2">AVENOIR // DEEP-SPACE NODE</text>
"""
    save("footer.svg", body, W, H)


if __name__ == "__main__":
    header()
    divider()
    whoami()
    radar()
    skills()
    footer()
