"""Dana Thrive — Deep Green Natural business card (final print build)."""
import math, os
import segno
from build import BASE_CSS, A, ROOT, icon

GREEN_BG = "#173329"      # deep forest ground
GREEN_LIFT = "#1F4234"    # soft centre lift
GOLD = "#D8BA7A"          # metallic-look gold (print ink)
GOLD_LT = "#E6CF9C"
CREAM = "#F3ECDD"         # body text on green (contrast ≈ 12:1)
CREAM_MUTED = "#D4CBB7"   # secondary text (contrast ≈ 9:1)

C = dict(
    sub="Disability Support Services",
    tagline="Support that builds on your strengths",
    phone="0415 163 252", email="info@danathrive.com.au", web="danathrive.com.au", loc="Melbourne, Victoria",
    ig="@DanaThrive", tt="@DanaThrive", fb="Dana Thrive",
    services=["Disability Support", "Community Participation", "Daily Living", "Group Activities"],
)
URL = "https://danathrive.com.au/"


# ---------------------------------------------------------------- leaves (vector)
_LID = 0


def leaf(x, y, length, width, angle, fill_id, vein="#5E8A63", vein_op=0.35, curve=0.12):
    """Botanical leaf with midrib and paired veins, base at (x,y), pointing at `angle` deg."""
    L, W = length, width
    c = curve * L
    outline = (f"M0 0 C{0.25*L:.2f} {-W*1.05 + c:.2f} {0.72*L:.2f} {-W*0.85 + c:.2f} {L:.2f} {c*1.2:.2f} "
               f"C{0.72*L:.2f} {W*0.75 + c:.2f} {0.28*L:.2f} {W*0.95 + c*0.6:.2f} 0 0Z")
    mid = f"M0 0 Q{0.5*L:.2f} {c*0.9:.2f} {L*0.98:.2f} {c*1.18:.2f}"
    veins = []
    for i in range(1, 9):
        t = i / 9.6
        px, py = t * L, c * 0.9 * (2 * t * (1 - t)) * 1.0 + c * 1.18 * t * t
        reach = W * 0.85 * math.sin(math.pi * min(t + 0.05, 1)) ** 0.8
        for s in (-1, 1):
            ex, ey = px + reach * 0.85, py + s * reach
            veins.append(f"M{px:.2f} {py:.2f} Q{px + reach*0.25:.2f} {py + s*reach*0.65:.2f} {ex:.2f} {ey:.2f}")
    global _LID; _LID += 1; cid = f"lc{_LID}"
    return (f'<g transform="translate({x} {y}) rotate({angle})"><clipPath id="{cid}"><path d="{outline}"/></clipPath>'
            f'<path d="{outline}" fill="url(#{fill_id})"/><g clip-path="url(#{cid})">'
            f'<path d="{mid}" fill="none" stroke="{vein}" stroke-opacity="{vein_op+0.15}" stroke-width="0.32" stroke-linecap="round"/>'
            f'<path d="{" ".join(veins)}" fill="none" stroke="{vein}" stroke-opacity="{vein_op}" stroke-width="0.16" stroke-linecap="round"/></g>'
            f'<path d="{outline}" fill="none" stroke="#6F9A70" stroke-opacity="0.25" stroke-width="0.15"/></g>')


DEFS = """<defs>
<linearGradient id="lfA" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3C6B48"/><stop offset="1" stop-color="#1E3F2C"/></linearGradient>
<linearGradient id="lfB" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#2E5A3B"/><stop offset="1" stop-color="#173826"/></linearGradient>
<linearGradient id="lfC" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#25493A"/><stop offset="1" stop-color="#1A3A2B"/></linearGradient>
</defs>"""


def svg_layer(content):
    # 96 x 61 mm card incl. bleed, user units = mm
    return (f'<svg class="art" viewBox="0 0 96 61" xmlns="http://www.w3.org/2000/svg" '
            f'style="position:absolute;inset:0;width:96mm;height:61mm">{DEFS}{content}</svg>')


# ---------------------------------------------------------------- QR (ECC H, centre mark)
def qr_svg(size_mm, dark):
    q = segno.make(URL, error="h", micro=False, boost_error=False)
    rows = [list(r) for r in q.matrix_iter(border=0)]
    n = len(rows)
    hole = 9 if n >= 33 else 7                    # centre clear zone in modules (≈7% of area at V4)
    h0 = (n - hole) // 2
    d = []
    for y, r in enumerate(rows):
        for x, v in enumerate(r):
            if v and not (h0 <= x < h0 + hole and h0 <= y < h0 + hole):
                d.append(f"M{x} {y}h1v1h-1z")
    m = size_mm / n
    mark = (f'<rect x="{h0+0.5}" y="{h0+0.5}" width="{hole-1}" height="{hole-1}" rx="1.4" fill="{dark}"/>'
            f'<image href="{A}/gold-icon.png" x="{h0+1.1}" y="{h0+1.1}" width="{hole-2.2}" height="{hole-2.2}"/>')
    return q.version, n, m, (f'<svg class="qr" viewBox="0 0 {n} {n}" shape-rendering="crispEdges" '
                             f'xmlns="http://www.w3.org/2000/svg"><path fill="{dark}" d="{"".join(d)}"/>{mark}</svg>')


CSS = BASE_CSS + f"""
.card{{background:radial-gradient(120% 140% at 50% 45%, {GREEN_LIFT} 0%, {GREEN_BG} 62%)}}
.gold{{color:{GOLD}}}
.caps{{text-transform:uppercase}}
.ic{{width:3mm;height:3mm}}
"""


FOIL_SEL = {"front": ".mark, .wm, .rule, .tag",
            "back": ".wm, .ci, .vr, .socials .ic, .hr, .services .sep, .sweep"}


def foil_css(side, mode):
    """mode: print (all CMYK) | nofoil (CMYK minus foil elements) | foil (100% K foil mask)."""
    sel = FOIL_SEL[side]
    if mode == "nofoil":
        return f"{sel}{{visibility:hidden !important}}"
    if mode == "foil":
        each = ", ".join(f"{s.strip()} *" for s in sel.split(","))
        return (f".card{{background:#fff !important}} .card *{{visibility:hidden}} "
                f"{sel}, {each}{{visibility:visible !important;color:#000 !important;opacity:1 !important}} "
                f".rule, .vr, .hr{{background:#000 !important}} .sweep{{stroke:#000 !important;stroke-opacity:1 !important}}")
    return ""


def page(css, body, marks=False):
    if not marks:
        return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{css}</style></head>'
                f'<body><div class="card">{body}</div></body></html>')
    # printer's sheet: 6mm slug around the bleed with crop marks at the trim lines
    M = 6
    lines = []
    for x in (3, 93):
        lines += [f'<line x1="{M+x}" y1="0" x2="{M+x}" y2="{M-1}"/>', f'<line x1="{M+x}" y1="{M+62}" x2="{M+x}" y2="{2*M+61}"/>']
    for y in (3, 58):
        lines += [f'<line x1="0" y1="{M+y}" x2="{M-1}" y2="{M+y}"/>', f'<line x1="{M+97}" y1="{M+y}" x2="{2*M+96}" y2="{M+y}"/>']
    W, H = 96 + 2 * M, 61 + 2 * M
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{css}'
            f'@page{{size:{W}mm {H}mm;margin:0}} html,body{{width:{W}mm;height:{H}mm;background:#fff}}'
            f'.card{{position:absolute;left:{M}mm;top:{M}mm}}</style></head><body>'
            f'<svg style="position:absolute;inset:0;width:{W}mm;height:{H}mm" viewBox="0 0 {W} {H}">'
            f'<g stroke="#000" stroke-width="0.12">{"".join(lines)}</g></svg>'
            f'<div class="card">{body}</div></body></html>')


# ---------------------------------------------------------------- FRONT
def front(marks=False, mode="print"):
    art = svg_layer(
        # top-left cluster (bleeds off the corner)
        leaf(-6, 20, 30, 7.5, -38, "lfC", vein_op=0.25)
        + leaf(-4, 34, 36, 9, -62, "lfA")
        + leaf(-2, 12, 22, 5.5, -14, "lfB", vein_op=0.3)
        # bottom-right cluster
        + leaf(104, 54, 24, 6, 160, "lfC", vein_op=0.25)
        + leaf(102, 68, 28, 7, 214, "lfA")
        + leaf(86, 67, 15, 4, 250, "lfB", vein_op=0.3)
    )
    css = f"""
.mark{{position:absolute;left:50%;top:5.6mm;height:21mm;transform:translateX(-50%)}}
.wm{{position:absolute;left:50%;top:28.4mm;width:42mm;transform:translateX(-50%)}}
.sub{{position:absolute;left:0;right:0;top:36.3mm;text-align:center;font-size:6.6pt;font-weight:500;
      letter-spacing:0.24em;color:{CREAM_MUTED};padding-left:0.24em}}
.rule{{position:absolute;left:50%;top:41.2mm;width:9mm;height:0.3mm;background:{GOLD};transform:translateX(-50%);opacity:.9}}
.tag{{position:absolute;left:0;right:0;top:44.2mm;text-align:center;font-size:7.2pt;font-weight:500;
      letter-spacing:0.14em;color:{GOLD_LT};padding-left:0.14em;white-space:nowrap}}
"""
    body = (art + f'<div class="trim"><img class="mark" src="{A}/gold-icon.png" alt="">'
            f'<img class="wm" src="{A}/gold-wordmark.png" alt="Dana Thrive">'
            f'<p class="sub caps">{C["sub"]}</p><div class="rule"></div>'
            f'<p class="tag caps">{C["tagline"]}</p></div>')
    html = page(css + foil_css("front", mode), body, marks)
    return html.replace("gold-icon.png", "foil-icon.png").replace("gold-wordmark.png", "foil-wordmark.png") if mode == "foil" else html


# ---------------------------------------------------------------- BACK
def back(marks=False, mode="print"):
    ver, n, m, qr = qr_svg(18.0, GREEN_BG)
    qz = m * 4
    tile = 18.0 + 2 * qz
    art = svg_layer(
        leaf(100, 4, 28, 7, 160, "lfC", vein_op=0.25)
        + leaf(98, -4, 30, 7.5, 128, "lfA")
        + leaf(88, -5, 18, 4.5, 105, "lfB", vein_op=0.3)
        # fine gold sweep hugging the leaf cluster
        + f'<path class="sweep" d="M66 -3 C74 1.5 84 4 90 9.5 C93.5 13 95.5 19 100 25" fill="none" stroke="{GOLD}" stroke-width="0.35" stroke-opacity="0.85" stroke-linecap="round"/>'
    )
    rows = [("phone", C["phone"]), ("envelope-simple", C["email"]), ("globe-simple", C["web"]), ("map-pin", C["loc"])]
    contacts = "".join(f'<li><span class="ci">{icon(i, "fill")}</span><span class="nowrap">{t}</span></li>' for i, t in rows)
    socials = "".join(f'<li>{icon(i, "fill")}<span class="nowrap">{t}</span></li>'
                      for i, t in [("instagram-logo", C["ig"]), ("tiktok-logo", C["tt"]), ("facebook-logo", C["fb"])])
    sep = f'<span class="sep">&bull;</span>'
    css = f"""
.wm{{position:absolute;left:5mm;top:5.4mm;width:33mm}}
.sub{{position:absolute;left:5.1mm;top:11.7mm;font-size:6pt;font-weight:500;letter-spacing:0.22em;color:{CREAM_MUTED};white-space:nowrap}}
.contacts{{position:absolute;left:5mm;top:16.6mm;list-style:none;display:flex;flex-direction:column;gap:1.75mm}}
.contacts li{{display:flex;align-items:center;gap:2.2mm;font-size:8pt;line-height:1;color:{CREAM};font-weight:400;letter-spacing:0.01em}}
.ci{{color:{GOLD};display:flex}}
.vr{{position:absolute;left:58.5mm;top:15mm;width:0.3mm;height:21mm;background:{GOLD};opacity:.55}}
.qrwrap{{position:absolute;right:5mm;top:12.4mm;width:{tile:.2f}mm}}
.qrtile{{width:{tile:.2f}mm;height:{tile:.2f}mm;padding:{qz:.3f}mm;background:{CREAM};border-radius:1.2mm}}
.qrlabel{{margin-top:1.2mm;text-align:center;font-size:6.4pt;font-weight:500;color:{CREAM_MUTED};letter-spacing:0.03em;white-space:nowrap}}
.socials{{position:absolute;left:5mm;right:5mm;top:40.6mm;list-style:none;display:flex;justify-content:space-between}}
.socials li{{display:flex;align-items:center;gap:1.4mm;font-size:7pt;line-height:1;color:{CREAM}}}
.socials .ic{{width:2.9mm;height:2.9mm;color:{GOLD}}}
.hr{{position:absolute;left:5mm;right:5mm;top:45.1mm;height:0.3mm;background:{GOLD};opacity:.55}}
.services{{position:absolute;left:5mm;right:5mm;top:47mm;text-align:center;font-size:6.1pt;font-weight:500;color:{CREAM_MUTED};white-space:nowrap;line-height:1}}
.services .sep{{color:{GOLD};margin:0 1.1mm}}
"""
    body = (art + f'<div class="trim"><img class="wm" src="{A}/gold-wordmark.png" alt="Dana Thrive">'
            f'<p class="sub caps">{C["sub"]}</p>'
            f'<ul class="contacts">{contacts}</ul><div class="vr"></div>'
            f'<div class="qrwrap"><div class="qrtile">{qr}</div><p class="qrlabel">Scan to learn more</p></div>'
            f'<ul class="socials">{socials}</ul><div class="hr"></div>'
            f'<p class="services">{sep.join(C["services"])}</p></div>')
    html = page(css + foil_css("back", mode), body, marks)
    if mode == "foil":
        html = html.replace("gold-wordmark.png", "foil-wordmark.png")
    return html, ver, n, m


if __name__ == "__main__":
    os.makedirs(f"{ROOT}/html", exist_ok=True)
    open(f"{ROOT}/html/dg-front.html", "w").write(front())
    open(f"{ROOT}/html/dg-front-marks.html", "w").write(front(True))
    b, ver, n, m = back()
    open(f"{ROOT}/html/dg-back.html", "w").write(b)
    open(f"{ROOT}/html/dg-back-marks.html", "w").write(back(True)[0])
    for mode in ("nofoil", "foil"):
        open(f"{ROOT}/html/dg-front-{mode}.html", "w").write(front(False, mode))
        open(f"{ROOT}/html/dg-back-{mode}.html", "w").write(back(False, mode)[0])
    print(f"QR: version {ver}, ECC H, {n} modules, module {m:.3f} mm, code 18 mm, quiet zone {4*m:.2f} mm")
