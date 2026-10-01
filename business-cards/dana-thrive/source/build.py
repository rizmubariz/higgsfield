"""Dana Thrive business card builder.

Generates print HTML (96 x 61 mm = 90 x 55 mm trim + 3 mm bleed) for each
concept/side. Rendered to PDF/PNG by render.mjs.
"""
import json, os, re, sys
import segno

ROOT = os.path.dirname(os.path.abspath(__file__))
A = f"file://{ROOT}/assets"
PH = os.path.join(ROOT, "..", "package", "assets")

# ---- brand tokens (from danathrive-websitee/app/src/site.css) -------------
NAVY, NAVY_DEEP, INK_DEEP = "#064A78", "#043A5F", "#042842"
TEAL, TEAL_TEXT, GREEN = "#0087A3", "#006F86", "#00885A"
PURPLE, LIME, GOLD = "#6F3CC3", "#86C93D", "#F4B41A"
INK, MUTED, LINE, SOFT = "#14263A", "#4A5B6D", "#DDE4EA", "#F5F7F9"

# ---- content --------------------------------------------------------------
C = dict(
    name="[Your Full Name]",
    title="Founder &amp; Director",
    company="Dana Thrive",
    phone="0415 163 252",
    email="info@danathrive.com.au",
    web="danathrive.com.au",
    loc="Melbourne, Victoria",
    tagline="Support that builds on your strengths",
    services=["Disability Support", "Community Participation", "Daily Living", "Group Activities"],
    ig="[Instagram handle]", tt="[TikTok handle]", fb="[Facebook page]",
)


def icon(name, weight="regular"):
    fn = f"{name}.svg" if weight == "regular" else f"{name}-{weight}.svg"
    svg = open(os.path.join(PH, weight, fn)).read()
    return svg.replace("<svg ", '<svg class="ic" aria-hidden="true" ', 1)


def qr_svg(dark):
    q = segno.make("https://danathrive.com.au/", error="m", micro=False)
    rows = list(q.matrix_iter(border=0))
    n = len(rows)
    d = "".join(f"M{x} {y}h1v1h-1z" for y, r in enumerate(rows) for x, v in enumerate(r) if v)
    return n, (f'<svg class="qr" viewBox="0 0 {n} {n}" shape-rendering="crispEdges" '
               f'xmlns="http://www.w3.org/2000/svg"><path fill="{dark}" d="{d}"/></svg>')


QR_N, _ = qr_svg("#000")

SPARKLE = ('<svg class="spk" viewBox="0 0 60 60" aria-hidden="true"><path fill="currentColor" '
           'd="M30 4 C31.5 20 35 26.5 56 30 C35 33.5 31.5 40 30 56 C28.5 40 25 33.5 4 30 C25 26.5 28.5 20 30 4Z"/></svg>')
UNDERLINE = ('<svg class="uline" viewBox="0 0 200 20" preserveAspectRatio="none" aria-hidden="true">'
             '<path d="M4 13 C46 6 98 5 196 10" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/></svg>')
BARS = [(NAVY, 12), (TEAL, 8), (GREEN, 6), (PURPLE, 3), (LIME, 3)]  # og-card spectrum


def bars(h="0.9mm", gap="0.9mm", unit=1.0):
    return ('<div class="bars" style="display:flex;gap:%s">' % gap + "".join(
        f'<span style="display:block;width:{w*unit:.2f}mm;height:{h};border-radius:{h};background:{c}"></span>'
        for c, w in BARS) + "</div>")


def edge(h="1.1mm", where="bottom"):
    """Five-colour spectrum edge running bleed-to-bleed."""
    total = sum(w for _, w in BARS)
    segs = "".join(f'<span style="flex:{w};background:{c}"></span>' for c, w in BARS)
    return f'<div class="edge" style="position:absolute;left:0;right:0;{where}:0;height:calc({h} + 3mm);display:flex">{segs}</div>'


BASE_CSS = f"""
@font-face{{font-family:Outfit;font-weight:300;src:url({A}/Outfit-300.ttf)}}
@font-face{{font-family:Outfit;font-weight:400;src:url({A}/Outfit-400.ttf)}}
@font-face{{font-family:Outfit;font-weight:500;src:url({A}/Outfit-500.ttf)}}
@font-face{{font-family:Outfit;font-weight:600;src:url({A}/Outfit-600.ttf)}}
@font-face{{font-family:Outfit;font-weight:700;src:url({A}/Outfit-700.ttf)}}
@page{{size:96mm 61mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:96mm;height:61mm;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{font-family:Outfit,sans-serif;color:{INK};-webkit-font-smoothing:antialiased;font-kerning:normal}}
.card{{position:relative;width:96mm;height:61mm;overflow:hidden;background:#fff}}
/* trim box = 90x55 at (3,3); safe area = 5mm inside trim */
.trim{{position:absolute;left:3mm;top:3mm;width:90mm;height:55mm}}
.ic{{width:2.5mm;height:2.5mm;flex:none;display:block}}
.spk{{display:inline-block;width:2.2mm;height:2.2mm}}
.qr{{display:block;width:100%;height:100%}}
.nowrap{{white-space:nowrap}}
/* guides (preview only) */
.guides .g{{position:absolute;pointer-events:none}}
.guides .g-trim{{left:3mm;top:3mm;width:90mm;height:55mm;outline:0.1mm solid #e0218a}}
.guides .g-safe{{left:8mm;top:8mm;width:80mm;height:45mm;outline:0.1mm dashed #00a2ff}}
"""


def page(css, body, guides=False):
    g = ('<div class="g g-trim"></div><div class="g g-safe"></div>' if guides else "")
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}{css}</style></head>'
            f'<body class="{"guides" if guides else ""}"><div class="card">{body}{g}</div></body></html>')


def qr_block(dark, tile_bg, label_color, extra=""):
    """QR at 17mm with a 4-module quiet zone on a light tile."""
    code = 17.0
    qz = code / QR_N * 4  # 4-module quiet zone
    _, svg = qr_svg(dark)
    tile = code + 2 * qz
    return (f'<div class="qrwrap" style="width:{tile:.2f}mm">'
            f'<div class="qrtile" style="width:{tile:.2f}mm;height:{tile:.2f}mm;padding:{qz:.2f}mm;background:{tile_bg};{extra}">{svg}</div>'
            f'<div class="qrlabel" style="color:{label_color}">Scan to learn more</div></div>')


def contacts(cls=""):
    rows = [("phone", C["phone"]), ("envelope-simple", C["email"]), ("globe-simple", C["web"]), ("map-pin", C["loc"])]
    return '<ul class="contacts %s">' % cls + "".join(
        f'<li><span class="ci ci-{n.split("-")[0]}">{icon(n)}</span><span class="nowrap">{t}</span></li>' for n, t in rows) + "</ul>"


def contacts_badged():
    rows = [("phone", C["phone"], GREEN), ("envelope-simple", C["email"], TEAL),
            ("globe-simple", C["web"], PURPLE), ("map-pin", C["loc"], NAVY)]
    return '<ul class="contacts">' + "".join(
        f'<li><span class="badge" style="background:{c}">{icon(n, "fill")}</span><span class="nowrap">{t}</span></li>'
        for n, t, c in rows) + "</ul>"


def socials():
    rows = [("instagram-logo", C["ig"]), ("tiktok-logo", C["tt"]), ("facebook-logo", C["fb"])]
    return '<ul class="socials">' + "".join(
        f'<li>{icon(n)}<span class="nowrap">{t}</span></li>' for n, t in rows) + "</ul>"


def services(sep_color):
    sep = f'<span class="sep" style="color:{sep_color}">&bull;</span>'
    return f'<p class="services nowrap">{sep.join(C["services"])}</p>'


SHARED_BACK_CSS = """
.contacts{list-style:none;display:flex;flex-direction:column;gap:1.25mm}
.contacts li{display:flex;align-items:center;gap:1.6mm;font-size:7pt;line-height:1.1;font-weight:400}
.socials{list-style:none;display:flex;gap:2.6mm}
.socials li{display:flex;align-items:center;gap:0.9mm;font-size:6pt;line-height:1}
.socials .ic{width:2.3mm;height:2.3mm}
.qrlabel{margin-top:1.2mm;font-size:6pt;font-weight:500;text-align:center;letter-spacing:0.02em;white-space:nowrap}
.services{font-size:6pt;font-weight:500;letter-spacing:0.01em;line-height:1}
.services .sep{margin:0 1.1mm}
.name{font-size:11pt;font-weight:600;line-height:1.05;letter-spacing:-0.01em}
.role{font-size:7.5pt;font-weight:500;line-height:1.2;margin-top:0.8mm}
.co{font-size:7pt;font-weight:400;line-height:1.2}
"""

# =========================================================================
# CONCEPT 1 — PREMIUM MINIMAL
# =========================================================================
def c1_front():
    css = f"""
.card{{background:#fff}}
.logo{{position:absolute;left:50%;top:9.2mm;height:28.5mm;transform:translateX(-50%)}}
.tag{{position:absolute;left:0;right:0;top:41.6mm;text-align:center;font-size:7.5pt;font-weight:400;
      color:{MUTED};letter-spacing:0.035em}}
.tag .spk{{color:{GOLD};width:1.9mm;height:1.9mm;vertical-align:-0.15mm;margin:0 1.4mm}}
"""
    body = (f'<div class="trim"><img class="logo" src="{A}/logo-full.png" alt="Dana Thrive">'
            f'<p class="tag">{C["tagline"]}</p></div>{edge("1.0mm")}')
    return page(css, body)


def c1_back():
    css = SHARED_BACK_CSS + f"""
.card{{background:#fff}}
.left{{position:absolute;left:5mm;top:5.2mm}}
.name{{color:{NAVY}}} .role{{color:{TEAL_TEXT}}} .co{{color:{MUTED}}}
.rule{{width:7mm;height:0.45mm;border-radius:0.3mm;background:{GOLD};margin:2.6mm 0 2.6mm}}
.contacts li{{color:{INK}}} .ci{{color:{NAVY}}}
.soc{{position:absolute;left:5mm;top:38.6mm}}
.socials li{{color:{MUTED}}}
.right{{position:absolute;right:5mm;top:5mm}}
.qrtile{{border:0.2mm solid {LINE};border-radius:1.4mm}}
.foot{{position:absolute;left:5mm;right:5mm;top:44.3mm;border-top:0.2mm solid {LINE};padding-top:1.7mm;
       display:flex;justify-content:center;color:{MUTED}}}
"""
    body = (f'<div class="trim">'
            f'<div class="left"><p class="name">{C["name"]}</p><p class="role">{C["title"]}</p><p class="co">{C["company"]}</p>'
            f'<div class="rule"></div>{contacts()}</div>'
            f'<div class="soc">{socials()}</div>'
            f'<div class="right">{qr_block(INK_DEEP, "#fff", MUTED)}</div>'
            f'<div class="foot">{services(TEAL)}</div>'
            f'</div>{edge("1.0mm")}')
    return page(css, body)


# =========================================================================
# CONCEPT 2 — MODERN BRAND
# =========================================================================
def c2_front():
    css = f"""
.card{{background:#fff}}
.panel{{position:absolute;top:0;bottom:0;right:0;left:{3+46}mm;background:{NAVY}}}
.logo{{position:absolute;left:5.6mm;top:50%;height:31mm;transform:translateY(-50%)}}
.tagwrap{{position:absolute;left:51.5mm;top:50%;transform:translateY(-54%);right:4.5mm}}
.tagwrap .spk{{color:{GOLD};width:2.6mm;height:2.6mm;display:block;margin-bottom:2.4mm}}
.tag{{color:#fff;font-size:13pt;font-weight:600;line-height:1.1;letter-spacing:-0.02em}}
.tagwrap .bars{{margin-top:4.6mm}}
.hl{{position:relative;display:inline-block;color:#fff}}
.hl .uline{{position:absolute;left:-0.3mm;right:-0.6mm;bottom:-1.3mm;height:1.6mm;width:auto;color:{GOLD}}}
"""
    tag = 'Support that<br>builds on your<br><span class="hl">strengths' + UNDERLINE + "</span>"
    lighter = [("#ffffff", 12), (TEAL, 8), (GREEN, 6), (PURPLE, 3), (LIME, 3)]
    b = '<div class="bars" style="display:flex;gap:0.9mm">' + "".join(
        f'<span style="display:block;width:{w*0.62:.2f}mm;height:0.9mm;border-radius:1mm;background:{c}"></span>'
        for c, w in lighter) + "</div>"
    body = (f'<div class="panel"></div>'
            f'<div class="trim"><img class="logo" src="{A}/logo-full.png" alt="Dana Thrive">'
            f'<div class="tagwrap">{SPARKLE}<p class="tag">{tag}</p>{b}</div></div>')
    return page(css, body)


def c2_back():
    stripe = "".join(f'<span style="flex:1;background:{c}"></span>' for c in (NAVY, TEAL, GREEN, PURPLE, LIME))
    css = SHARED_BACK_CSS + f"""
.card{{background:#fff}}
.stripe{{position:absolute;left:0;top:0;bottom:0;width:{3+2.2}mm;display:flex;flex-direction:column}}
.left{{position:absolute;left:7mm;top:5.2mm}}
.name{{color:{NAVY};font-weight:700}} .role{{color:{GREEN};font-weight:600}} .co{{color:{MUTED}}}
.contacts{{margin-top:3mm;gap:1.15mm}}
.badge{{display:flex;align-items:center;justify-content:center;width:3.3mm;height:3.3mm;border-radius:50%;color:#fff;flex:none}}
.badge .ic{{width:1.9mm;height:1.9mm}}
.contacts li{{color:{INK};gap:1.5mm}}
.soc{{position:absolute;left:7mm;top:38.8mm}}
.socials li{{color:{NAVY}}}
.right{{position:absolute;right:5mm;top:5mm}}
.qrtile{{border-radius:1.6mm;box-shadow:inset 0 0 0 0.25mm {LINE}}}
.qrlabel .spk{{color:{GOLD};width:1.6mm;height:1.6mm;vertical-align:-0.1mm;margin-right:0.8mm}}
.band{{position:absolute;left:{3+2.2}mm;right:0;bottom:0;height:{3+9.8}mm;background:{SOFT}}}
.foot{{position:absolute;left:7mm;right:5mm;top:{55-9.8+2.1}mm;display:flex;justify-content:flex-start;color:{NAVY}}}
"""
    qr = qr_block(NAVY, "#fff", NAVY).replace("Scan to learn more", SPARKLE + "Scan to learn more")
    body = (f'<div class="stripe">{stripe}</div><div class="band"></div>'
            f'<div class="trim">'
            f'<div class="left"><p class="name">{C["name"]}</p><p class="role">{C["title"]}</p><p class="co">{C["company"]}</p>'
            f'{contacts_badged()}</div>'
            f'<div class="soc">{socials()}</div>'
            f'<div class="right">{qr}</div>'
            f'<div class="foot">{services(TEAL)}</div>'
            f'</div>')
    return page(css, body)


# =========================================================================
# CONCEPT 3 — EXECUTIVE DARK
# =========================================================================
ON_DARK = "#E8EFF5"
ON_DARK_MUTED = "#A7BACB"


def c3_front():
    css = f"""
.card{{background:{INK_DEEP}}}
.wm{{position:absolute;right:-17mm;bottom:-20mm;width:46mm;height:46mm;opacity:0.32}}
.wm svg{{width:100%;height:100%;display:block}}
.plate{{position:absolute;left:5.5mm;top:50%;transform:translateY(-50%);width:38mm;height:37mm;background:#fff;
        border-radius:2.4mm;display:flex;align-items:center;justify-content:center}}
.plate img{{height:29.5mm}}
.tagwrap{{position:absolute;left:48mm;right:4.5mm;top:50%;transform:translateY(-50%)}}
.tag{{color:#fff;font-size:10.5pt;font-weight:300;line-height:1.22;letter-spacing:0.005em}}
.tag b{{font-weight:600;color:#fff}}
.goldrule{{width:8mm;height:0.4mm;background:{GOLD};border-radius:0.3mm;margin:0 0 3mm}}
.tagwrap .bars{{margin-top:3.4mm}}
"""
    wm = ('<svg viewBox="0 0 60 60"><path fill="none" stroke="%s" stroke-width="0.22" '
          'd="M30 4 C31.5 20 35 26.5 56 30 C35 33.5 31.5 40 30 56 C28.5 40 25 33.5 4 30 C25 26.5 28.5 20 30 4Z"/></svg>' % GOLD)
    lead = [("#ffffff", 12), (TEAL, 8), (GREEN, 6), (PURPLE, 3), (LIME, 3)]
    b = '<div class="bars" style="display:flex;gap:0.8mm">' + "".join(
        f'<span style="display:block;width:{w*0.55:.2f}mm;height:0.7mm;border-radius:1mm;background:{c}"></span>' for c, w in lead) + "</div>"
    body = (f'<div class="trim">'
            f'<div class="plate"><img src="{A}/logo-full.png" alt="Dana Thrive"></div>'
            f'<div class="tagwrap"><div class="goldrule"></div>'
            f'<p class="tag">Support that builds on your <b>strengths</b></p>{b}</div></div>')
    return page(css, body)


def c3_back():
    css = SHARED_BACK_CSS + f"""
.card{{background:{INK_DEEP}}}
.left{{position:absolute;left:5mm;top:5.2mm}}
.name{{color:#fff}} .role{{color:{GOLD}}} .co{{color:{ON_DARK_MUTED}}}
.rule{{width:100%;height:0.2mm;background:rgba(255,255,255,0.16);margin:2.6mm 0 2.6mm}}
.contacts li{{color:{ON_DARK}}} .ci{{color:#5FC4DA}}
.soc{{position:absolute;left:5mm;top:38.6mm}}
.socials li{{color:{ON_DARK_MUTED}}}
.right{{position:absolute;right:5mm;top:5mm}}
.qrtile{{border-radius:1.6mm}}
.foot{{position:absolute;left:5mm;right:5mm;top:44.3mm;border-top:0.2mm solid rgba(255,255,255,0.16);padding-top:1.7mm;
       display:flex;justify-content:center;color:{ON_DARK_MUTED}}}
"""
    body = (f'<div class="trim">'
            f'<div class="left"><p class="name">{C["name"]}</p><p class="role">{C["title"]}</p><p class="co">{C["company"]}</p>'
            f'<div class="rule"></div>{contacts()}</div>'
            f'<div class="soc">{socials()}</div>'
            f'<div class="right">{qr_block(INK_DEEP, "#fff", ON_DARK_MUTED)}</div>'
            f'<div class="foot">{services(GOLD)}</div>'
            f'</div>{edge("0.9mm")}')
    return page(css, body)


JOBS = {
    "c1-front": c1_front, "c1-back": c1_back,
    "c2-front": c2_front, "c2-back": c2_back,
    "c3-front": c3_front, "c3-back": c3_back,
}

if __name__ == "__main__":
    os.makedirs(f"{ROOT}/html", exist_ok=True)
    for k, fn in JOBS.items():
        html = fn()
        open(f"{ROOT}/html/{k}.html", "w").write(html)
        open(f"{ROOT}/html/{k}-guides.html", "w").write(html.replace('<body class="">', '<body class="guides">', 1)
                                                        .replace('</div></body>', '<div class="g g-trim"></div><div class="g g-safe"></div></div></body>'))
    print("built", list(JOBS), "QR modules:", QR_N)
