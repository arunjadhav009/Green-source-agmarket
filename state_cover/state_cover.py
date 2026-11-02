"""Cover (page_1) for single-state Hindi / English posts and the Hindi mix-state post.

generate_state_cover(state_name, post_date, records, output_path, lang)          lang = 'hi' | 'en'
generate_mix_cover(post_date, records, output_path)                               records carry '_State'
"""
import base64
import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_B64 = {}


def _b64(name):
    if name not in _B64:
        _B64[name] = base64.b64encode((ROOT / name).read_bytes()).decode()
    return _B64[name]


HINDI_STATE_NAMES = {
    "andhra pradesh": "आंध्र प्रदेश", "arunachal pradesh": "अरुणाचल प्रदेश", "assam": "असम",
    "bihar": "बिहार", "chhattisgarh": "छत्तीसगढ़", "chattisgarh": "छत्तीसगढ़", "goa": "गोवा",
    "gujarat": "गुजरात", "haryana": "हरियाणा", "himachal pradesh": "हिमाचल प्रदेश",
    "jharkhand": "झारखंड", "karnataka": "कर्नाटक", "kerala": "केरल", "madhya pradesh": "मध्य प्रदेश",
    "maharashtra": "महाराष्ट्र", "manipur": "मणिपुर", "meghalaya": "मेघालय", "mizoram": "मिजोरम",
    "nagaland": "नागालैंड", "odisha": "ओडिशा", "orissa": "ओडिशा", "punjab": "पंजाब",
    "rajasthan": "राजस्थान", "sikkim": "सिक्किम", "tamil nadu": "तमिलनाडु", "telangana": "तेलंगाना",
    "tripura": "त्रिपुरा", "uttar pradesh": "उत्तर प्रदेश", "uttarakhand": "उत्तराखंड",
    "uttrakhand": "उत्तराखंड", "west bengal": "पश्चिम बंगाल", "nct of delhi": "दिल्ली", "delhi": "दिल्ली",
    "jammu and kashmir": "जम्मू-कश्मीर", "jammu & kashmir": "जम्मू-कश्मीर", "chandigarh": "चंडीगढ़",
    "puducherry": "पुडुचेरी", "pondicherry": "पुडुचेरी", "ladakh": "लद्दाख",
    "andaman and nicobar": "अंडमान-निकोबार", "dadra and nagar haveli": "दादरा नगर हवेली",
}


def hindi_state(name):
    return HINDI_STATE_NAMES.get(str(name or "").strip().lower(), str(name or "").strip())


def parse_post_date(value):
    s = str(value or "").strip()[:10]
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date()


DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def pick_cta(date, lang):
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    block = c[lang]
    extra = block.get("rotating_cta") or []
    o = date.toordinal()
    if c.get("rotation_enabled") and extra and o % 2 == 1:
        return extra[(o // 2) % len(extra)]
    return block["primary_cta"][DAYS[date.weekday()]]


def _num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


def _top5(records):
    return sorted(records, key=lambda r: _num(r.get("MaxPrice")), reverse=True)[:5]


def _esc(s):
    return html.escape(str(s or "").strip())


def _t(id_, box, inner, size, cls="", minsize=16, style=""):
    x, y, w, h = box
    return (f'<div id="{id_}" class="t {cls}" data-min="{minsize}" '
            f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;font-size:{size}px;{style}">'
            f'<span>{inner}</span></div>')


ROWS = [  # name, location, price, unit  (from layout.json of the reference package)
    ([245, 516, 520, 43], [247, 558, 515, 33], [794, 516, 194, 50], [813, 568, 174, 26]),
    ([245, 603, 520, 43], [247, 645, 515, 33], [794, 603, 194, 50], [813, 655, 174, 26]),
    ([245, 689, 520, 43], [247, 731, 515, 33], [794, 689, 194, 50], [813, 741, 174, 26]),
    ([245, 776, 520, 43], [247, 818, 515, 33], [794, 776, 194, 50], [813, 828, 174, 26]),
    ([245, 863, 520, 43], [247, 905, 515, 33], [794, 863, 194, 50], [813, 915, 174, 26]),
]
CHIP_COLORS = ['#ffeb32', '#dc0041', '#008b08', '#7715b4', '#f08a00', '#0067d9',
               '#008cb3', '#b5101b', '#079c16', '#651b9c', '#e68000', '#f0f0ef']

CSS = """
@font-face{font-family:Noto;src:url('data:font/ttf;base64,__NOTO__');font-weight:100 900;font-display:block}
@font-face{font-family:Pop;src:url('data:font/ttf;base64,__POPB__');font-weight:700 900;font-display:block}
@font-face{font-family:Pop;src:url('data:font/ttf;base64,__POPM__');font-weight:400 600;font-display:block}
*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1350px;overflow:hidden;background:#2a0d24}
#p{position:relative;width:1080px;height:1350px;font-family:__FAM__;color:#fff}
#bg{position:absolute;inset:0;width:1080px;height:1350px}
.t{position:absolute;display:flex;align-items:center;line-height:1.15;font-weight:800;white-space:nowrap}
.t span{display:block;max-width:100%}
.c{justify-content:center;text-align:center}.r{justify-content:flex-end;text-align:right}
.w{white-space:normal;text-wrap:balance}
.sh{text-shadow:0 3px 0 #1a0010,0 0 10px rgba(0,0,0,.55)}
.y{color:#ffe62e}.dk{color:#350515}
.chip{position:absolute;border-radius:11px;border:2px solid #f0d9ef;box-shadow:inset 0 2px 0 rgba(255,255,255,.35)}
#cta .ico{display:inline-block;width:.9em;height:.9em;vertical-align:-.12em}
.cover{position:absolute;background:#2a0820}
"""

FIT = """<script>
window.__fit=async()=>{await document.fonts.ready;const problems=[];
for(const el of document.querySelectorAll('.t')){const sp=el.firstElementChild;
let s=parseFloat(getComputedStyle(el).fontSize);const min=Number(el.dataset.min||16);
const ok=()=>sp.scrollWidth<=el.clientWidth+1&&sp.getBoundingClientRect().height<=el.clientHeight+1;
while(!ok()&&s>min){s--;el.style.fontSize=s+'px'}if(!ok())problems.push(el.id)}
return {problems,noto:document.fonts.check('30px Noto'),pop:document.fonts.check('bold 30px Pop')}};
</script>"""


def _page(plate, layers, lang):
    fam = "Pop,Noto,sans-serif" if lang == "en" else "Noto,sans-serif"
    css = (CSS.replace("__NOTO__", _b64("fonts/NotoSansDevanagari.ttf"))
              .replace("__POPB__", _b64("fonts/Poppins-Bold.ttf"))
              .replace("__POPM__", _b64("fonts/Poppins-Medium.ttf"))
              .replace("__FAM__", fam))
    return (f'<!doctype html><html lang="{lang}"><meta charset="utf-8"><style>{css}</style>'
            f'<div id="p"><img id="bg" src="data:image/png;base64,{_b64(plate)}">'
            + "\n".join(layers) + "</div>" + FIT + "</html>")


def _rows(top, loc_fn, unit):
    out = []
    for i, r in enumerate(top):
        nb, lb, pb, ub = ROWS[i]
        col = "dk" if i == 0 else ""
        out.append(_t(f"m{i}", nb, _esc(r.get("Market")), 36, col, 20))
        out.append(_t(f"l{i}", lb, _esc(loc_fn(r)), 26, col, 15, "font-weight:500"))
        price = "₹" + format(int(round(_num(r.get("MaxPrice")))), ",")
        pc = "color:#87051f" if i == 0 else "color:#ffeb30"
        out.append(_t(f"p{i}", pb, price, 48, "r", 28, pc + ";font-weight:900;font-family:Pop,Noto"))
        out.append(_t(f"u{i}", ub, unit, 22, "r " + col, 14, "font-weight:500"))
    return out


def _common(date, lang, unit_label, measure_label):
    cta = _esc(pick_cta(date, lang))
    return [
        _t("date", [60, 112, 330, 60], date.strftime("%d-%m-%Y"), 48, "c", 34,
           "color:#130510;font-weight:900;font-family:Pop,Noto"),
        _t("cta", [400, 1046, 460, 110], cta, 38 if lang == "hi" else 34, "c w", 22,
           "color:#6d092c;font-weight:900;line-height:1.2"),
        '<div class="cover" style="left:84px;top:1262px;width:350px;height:36px"></div>',
        _t("foot", [86, 1262, 346, 36], f'{unit_label} <span style="color:#ffe62e;display:inline">•</span> {measure_label}',
           22, "", 14, "font-weight:600"),
    ]


def build_state_html(state_name, post_date, records, lang):
    date = parse_post_date(post_date)
    top = _top5(records)
    n = len({(str(r.get("Market")), str(r.get("District"))) for r in records})
    best = "₹" + format(int(round(_num(top[0].get("MaxPrice")))), ",") if top else ""
    if lang == "hi":
        st = hindi_state(state_name)
        layers = [
            _t("title", [45, 172, 740, 88], _esc(st), 92, "sh", 44, "font-weight:900"),
            _t("badge", [832, 30, 200, 92], f'<span style="color:#c8102e;display:block">{_esc(st)}</span>'
               '<span style="color:#101010;display:block">अपडेट</span>', 36, "c w", 20,
               "font-weight:900;line-height:1.05;transform:rotate(-4deg)"),
            _t("summary", [70, 410, 940, 86], f'आज <b class="y">{n}</b> मंडियों के भाव &nbsp;•&nbsp; '
               f'सबसे ऊंचा भाव <b class="y">{best}</b>', 34, "c", 20, "font-weight:700"),
        ]
        layers += _rows(top, lambda r: "जिला: " + str(r.get("District") or "").strip(), "प्रति क्विंटल")
        layers += _common(date, "hi", "प्रति क्विंटल", "अधिकतम बाजारभाव")
        return _page("plate_hi.png", layers, "hi")
    st = str(state_name or "").strip().title()
    layers = [
        _t("tag", [143, 62, 255, 30], "For Farmers' Trust", 22, "", 14, "font-weight:500"),
        _t("time", [528, 32, 182, 64], '<span style="display:block;font-size:.62em">Daily</span>'
           '<span class="y" style="display:block">7:30–8:30 PM</span>', 30, "c w", 14, "line-height:1.05"),
        _t("title", [45, 180, 740, 76], _esc(st), 74, "sh", 40, "font-weight:800"),
        _t("title2", [45, 258, 605, 84], "Onion Mandi Prices", 70, "sh y", 40, "font-weight:800"),
        _t("ribbon", [190, 348, 430, 42], 'Today\'s <span class="y" style="display:inline">Top 5</span> Highest Prices',
           26, "c", 16, "font-weight:700"),
        _t("badge", [832, 30, 200, 92], f'<span style="color:#c8102e;display:block">{_esc(st)}</span>'
           '<span style="color:#101010;display:block">UPDATE</span>', 32, "c w", 16,
           "font-weight:800;line-height:1.05;transform:rotate(-4deg)"),
        _t("summary", [70, 410, 940, 86], f'<b class="y">{n}</b> mandis checked today &nbsp;•&nbsp; '
           f'Highest <b class="y">{best}</b>', 32, "c", 18, "font-weight:700"),
        _t("cmt", [492, 966, 315, 66], "Comment Below", 40, "c", 22, "font-weight:800"),
        _t("cmt2", [522, 1158, 210, 50], "Write in comments", 26, "c", 14, "font-weight:700"),
        _t("next", [740, 1260, 270, 40], "All prices in next photo", 22, "c", 14, "color:#150916;font-weight:700"),
    ]
    layers += _rows(top, lambda r: "District: " + str(r.get("District") or "").strip(), "per quintal")
    layers += _common(date, "en", "Per Quintal", "Maximum Price")
    return _page("plate_en.png", layers, "en")


def build_mix_html(post_date, records):
    date = parse_post_date(post_date)
    top = _top5(records)
    states = []
    for r in records:
        s = hindi_state(r.get("_State"))
        if s and s not in states:
            states.append(s)
    limit = 11
    labels = states[:limit] if len(states) <= limit + 1 else states[:limit - 1] + [f"अन्य {len(states) - (limit - 1)} राज्य"]
    x, y, w, h = 243, 404, 762, 97
    cols = 6 if len(labels) > 8 else (4 if len(labels) > 4 else max(1, len(labels)))
    rows = 2 if len(labels) > cols else 1
    gap = 8
    cw, ch = (w - (cols - 1) * gap) // cols, (h - (rows - 1) * gap) // rows
    layers = []
    for i, lab in enumerate(labels):
        xx, yy = x + (i % cols) * (cw + gap), y + (i // cols) * (ch + gap)
        col = CHIP_COLORS[i % len(CHIP_COLORS)]
        dark = col in ("#ffeb32", "#f0f0ef")
        if lab.startswith("अन्य"):
            col, dark = "#f0f0ef", True
        layers.append(f'<div class="chip" style="left:{xx}px;top:{yy}px;width:{cw}px;height:{ch}px;background:{col}"></div>')
        layers.append(_t(f"chip{i}", [xx + 5, yy + 1, cw - 10, ch - 2], _esc(lab), 26, "c", 13,
                         ("color:#150916;" if dark else "") + "padding-top:5px"))
    layers += _rows(top, lambda r: f'{str(r.get("District") or "").strip()} · {hindi_state(r.get("_State"))}', "प्रति क्विंटल")
    layers += _common(date, "hi", "प्रति क्विंटल", "अधिकतम बाजारभाव")
    return _page("plate_mix.png", layers, "hi")


def _shoot(page_html, output_path, browser=None):
    def run(b):
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        pg.set_content(page_html, wait_until="load")
        rep = pg.evaluate("window.__fit()")
        if rep.get("problems"):
            print("⚠️ cover text shrunk to minimum:", rep["problems"])
        pg.screenshot(path=str(output_path), full_page=False)
        pg.close()
        return rep
    if browser is not None:
        return run(browser)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        try:
            return run(b)
        finally:
            b.close()


def generate_state_cover(state_name, post_date, records, output_path, lang, browser=None):
    return _shoot(build_state_html(state_name, post_date, records, lang), output_path, browser)


def generate_mix_cover(post_date, records, output_path, browser=None):
    return _shoot(build_mix_html(post_date, records), output_path, browser)
