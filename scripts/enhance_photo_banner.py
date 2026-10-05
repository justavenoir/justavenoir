import os
import base64
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.normpath(os.path.join(HERE, ".."))
ASSETS_DIR = os.path.join(REPO_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

SRC_PATH = r"C:\Users\Avenoir\.gemini\antigravity\brain\da3c3773-5696-4461-a522-a41f1b5cc81b\.user_uploaded\media_1791194597156.jpg"

def process_images():
    img = Image.open(SRC_PATH).convert("RGB")
    ow, oh = img.size
    print(f"Original photo size: {ow}x{oh}")

    # 1. High-Resolution Avatar (800x800)
    # Centered nicely on the silhouette on car + stars
    avatar_crop = img.crop((int(ow * 0.08), int(oh * 0.12), int(ow * 0.92), int(oh * 0.94)))
    avatar = avatar_crop.resize((800, 800), Image.Resampling.LANCZOS)
    avatar = ImageEnhance.Sharpness(avatar).enhance(1.35)
    avatar = ImageEnhance.Contrast(avatar).enhance(1.15)
    avatar_path = os.path.join(ASSETS_DIR, "avatar_hq.png")
    avatar.save(avatar_path, quality=96)
    print(f"Saved avatar: {avatar_path} (800x800)")

    # 2. High-Resolution Widescreen Banner (1200x540)
    BW, BH = 1200, 540
    crop_y1 = 90
    crop_y2 = 880
    cropped = img.crop((0, crop_y1, ow, crop_y2))
    cw, ch = cropped.size

    scale = BH / ch
    new_w = int(cw * scale)
    scaled = cropped.resize((new_w, BH), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (BW, BH), (5, 8, 16))
    offset_x = (BW - new_w) // 2
    canvas.paste(scaled, (offset_x, 0))

    # Feather side edges so they blend into deep cosmos
    fade_w = 70
    for i in range(fade_w):
        alpha = i / fade_w
        x_left = offset_x + i
        x_right = offset_x + new_w - 1 - i
        for y in range(BH):
            bg = np.array([5, 8, 16])
            pl = np.array(canvas.getpixel((x_left, y)))
            canvas.putpixel((x_left, y), tuple((pl * alpha + bg * (1 - alpha)).astype(np.uint8)))
            pr = np.array(canvas.getpixel((x_right, y)))
            canvas.putpixel((x_right, y), tuple((pr * alpha + bg * (1 - alpha)).astype(np.uint8)))

    # Feather bottom edge (last 35 pixels) to blend seamlessly into GitHub dark mode
    for y in range(BH - 35, BH):
        alpha = (BH - 1 - y) / 35.0
        for x in range(BW):
            p = np.array(canvas.getpixel((x, y)))
            bg = np.array([2, 4, 9])
            canvas.putpixel((x, y), tuple((p * alpha + bg * (1 - alpha)).astype(np.uint8)))

    # Enhance clarity and cosmic contrast
    canvas = ImageEnhance.Sharpness(canvas).enhance(1.3)
    canvas = ImageEnhance.Contrast(canvas).enhance(1.12)
    banner_png_path = os.path.join(ASSETS_DIR, "banner_photo_hq.png")
    canvas.save(banner_png_path, quality=96)
    print(f"Saved banner photo: {banner_png_path} ({BW}x{BH})")

    # 3. Locate bright star in banner
    gray = np.array(canvas.convert("L"))
    slice_reg = gray[40:180, 680:880]
    sy, sx = np.unravel_index(np.argmax(slice_reg), slice_reg.shape)
    star_x = 680 + sx
    star_y = 40 + sy
    print(f"Located star at: ({star_x}, {star_y})")

    # 4. Generate composite animated header.svg embedding the real photo
    with open(banner_png_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode("ascii")

    SCAN = "#a9e2d4"
    TEXT = "#ffffff"
    MUTED = "#8e99ac"
    DIM = "#3a4358"
    BEIGE = "#e2d5bd"
    ROSE = "#bb8c82"
    TEAL = "#86ad9f"
    FONT = "'JetBrains Mono','Fira Code',Consolas,monospace"
    tx, ty = 70, 200

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}" fill="none" xml:space="preserve">
<style>
text {{ font-family: {FONT}; white-space: pre; }}
.beam {{ animation: beam 6s linear infinite; }}
@keyframes beam {{ 0% {{ transform: translateY(-120px); }} 100% {{ transform: translateY({BH}px); }} }}
.lock {{ transform-origin: {star_x}px {star_y}px; animation: lock 5s ease-out infinite; }}
@keyframes lock {{ 0% {{ transform: scale(2.2) rotate(45deg); opacity: 0; }} 15% {{ transform: scale(1) rotate(0); opacity: 1; }} 80% {{ opacity: 1; }} 86% {{ opacity: .2; }} 90% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
.lockLabel {{ animation: lbl 5s steps(1) infinite; }}
@keyframes lbl {{ 0%, 15% {{ opacity: 0; }} 18%, 85% {{ opacity: 1; }} 87% {{ opacity: 0; }} 90%, 100% {{ opacity: 1; }} }}
.blink {{ animation: blink 1.1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.title {{ animation: flick 7s infinite; }}
@keyframes flick {{ 0%, 88%, 100% {{ opacity: 1; }} 89% {{ opacity: .55; }} 90% {{ opacity: 1; }} 94% {{ opacity: .7; }} 95% {{ opacity: 1; }} }}
.g1, .g2 {{ opacity: 0; animation: g1 7s steps(1) infinite; }}
.g2 {{ animation-name: g2; }}
@keyframes g1 {{ 0%,88% {{ opacity: 0; transform: none; }} 89% {{ opacity: .8; transform: translate(-4px, 1px); }} 90% {{ opacity: .5; transform: translate(2px, -2px); }} 91%,93% {{ opacity: 0; }} 94% {{ opacity: .7; transform: translate(-2px, 0); }} 95%,100% {{ opacity: 0; }} }}
@keyframes g2 {{ 0%,88% {{ opacity: 0; transform: none; }} 89% {{ opacity: .8; transform: translate(4px, -1px); }} 90% {{ opacity: .5; transform: translate(-2px, 2px); }} 91%,93% {{ opacity: 0; }} 94% {{ opacity: .7; transform: translate(2px, 1px); }} 95%,100% {{ opacity: 0; }} }}
</style>
<defs>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{SCAN}" stop-opacity="0"/>
  <stop offset=".85" stop-color="{SCAN}" stop-opacity=".06"/>
  <stop offset=".985" stop-color="{SCAN}" stop-opacity=".35"/>
  <stop offset="1" stop-color="{SCAN}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="leftFade" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#020409" stop-opacity=".75"/>
  <stop offset=".45" stop-color="#020409" stop-opacity=".4"/>
  <stop offset="1" stop-color="#020409" stop-opacity="0"/>
</linearGradient>
<radialGradient id="vig" cx=".5" cy=".45" r=".75">
  <stop offset=".55" stop-color="#000" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity=".7"/>
</radialGradient>
<pattern id="scanlines" width="4" height="3" patternUnits="userSpaceOnUse">
  <rect width="4" height="1" fill="#000" opacity=".25"/>
</pattern>
<filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
  <feGaussianBlur stdDeviation="3.5" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
</defs>

<!-- Enhanced Real Photograph Layer -->
<image href="data:image/png;base64,{b64_data}" x="0" y="0" width="{BW}" height="{BH}" preserveAspectRatio="xMidYMid slice"/>

<!-- Left Dark Gradient for Typography Legibility -->
<rect x="0" y="0" width="620" height="{BH}" fill="url(#leftFade)"/>

<!-- Scanlines overlay -->
<rect width="{BW}" height="{BH}" fill="url(#scanlines)" opacity=".25"/>

<!-- Animated Laser Scanner Beam -->
<rect class="beam" width="{BW}" height="120" fill="url(#beam)"/>

<!-- Cinematic Vignette -->
<rect width="{BW}" height="{BH}" fill="url(#vig)"/>

<!-- HUD Reticle Lock over REAL Star -->
<g class="lock" stroke="{SCAN}" stroke-width="1.5" fill="none">
  <path d="M{star_x-24},{star_y-14} V{star_y-24} H{star_x-14} M{star_x+14},{star_y-24} H{star_x+24} V{star_y-14} M{star_x+24},{star_y+14} V{star_y+24} H{star_x+14} M{star_x-14},{star_y+24} H{star_x-24} V{star_y+14}"/>
  <circle cx="{star_x}" cy="{star_y}" r="11" stroke="{SCAN}" stroke-dasharray="3 3" stroke-width="1"/>
</g>
<g class="lockLabel">
  <path d="M{star_x+24},{star_y-24} L{star_x+48},{star_y-40} H{star_x+170}" stroke="{SCAN}" stroke-opacity=".75" stroke-width="1" fill="none"/>
  <text x="{star_x+52}" y="{star_y-45}" font-size="11" fill="{SCAN}" letter-spacing="1">OBJ-01 · LOCKED</text>
  <text x="{star_x+52}" y="{star_y-26}" font-size="10" fill="{MUTED}">MAG -1.46 · TARGET ACQUIRED</text>
</g>

<!-- Corner HUD brackets -->
<path d="M16,38 V16 H38 M{BW-38},16 H{BW-16} V38 M{BW-16},{BH-38} V{BH-16} H{BW-38} M38,{BH-16} H16 V{BH-38}" stroke="{SCAN}" stroke-opacity=".65" stroke-width="1.5" fill="none"/>

<!-- Top Telemetry -->
<text x="44" y="46" font-size="12" fill="{MUTED}" letter-spacing="2">SYS://AVENOIR.DEEP-SPACE</text>
<text x="44" y="64" font-size="11" fill="{SCAN}" letter-spacing="1"><tspan class="blink">●</tspan> UPLINK ESTABLISHED</text>
<text x="{BW-44}" y="46" font-size="11" fill="{MUTED}" text-anchor="end" letter-spacing="1">RA 17h45m40s · DEC −29°00′28″</text>

<!-- Bottom Telemetry -->
<text x="44" y="{BH-30}" font-size="11" fill="{MUTED}" letter-spacing="1">SCAN MODE: ACTIVE · SECTOR 0x7E3</text>
<text x="{BW-44}" y="{BH-30}" font-size="11" fill="{MUTED}" text-anchor="end" letter-spacing="1">SIGNAL <tspan fill="{SCAN}">▮▮▮▮▮▮▮</tspan><tspan fill="{DIM}">▮</tspan> 88%</text>

<!-- Left-aligned Cinematic Typography -->
<g font-size="70" font-weight="700" letter-spacing="14">
  <text class="g1" x="{tx}" y="{ty}" fill="{TEAL}">AVENOIR</text>
  <text class="g2" x="{tx}" y="{ty}" fill="{ROSE}">AVENOIR</text>
  <text class="title" x="{tx}" y="{ty}" fill="{TEXT}" filter="url(#glow)">AVENOIR</text>
</g>
<line x1="{tx}" y1="{ty+18}" x2="{tx+380}" y2="{ty+18}" stroke="{BEIGE}" stroke-opacity=".5" stroke-width="1.5"/>
<text x="{tx}" y="{ty+46}" font-size="18" fill="{BEIGE}" letter-spacing="6">CYBERSECURITY ENGINEER</text>
<text x="{tx}" y="{ty+74}" font-size="12" fill="{MUTED}" letter-spacing="2">// SECURITY IS NOT A FEATURE. IT'S A MINDSET.</text>
<text x="{tx}" y="{ty+102}" font-size="11" fill="{SCAN}" letter-spacing="1">ORBIT: DEEP SPACE · EXPLORE &gt; BUILD &gt; SECURE</text>

</svg>"""

    header_svg_path = os.path.join(ASSETS_DIR, "header.svg")
    with open(header_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated animated header.svg: {header_svg_path} ({len(svg_content)//1024} KB)")

if __name__ == "__main__":
    process_images()
