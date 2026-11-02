"""महाराष्ट्राची पहिली (Top 5 कव्हर) इमेज — नवीन डिझाइन.

फक्त Maharashtra राज्यासाठी generate_images.py मधून वापरले जाते.
बाकी राज्ये, डेटा स्लाइड्स, caption, फाइलची नावे यात काहीही बदल नाही.
"""
import base64
import datetime as dt
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
WEEKDAYS_MR = ["सोमवार", "मंगळवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
ROW_TOPS = [365, 475, 577, 679, 781]
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]+")

CROWN_SVG = (
    '<svg id="crown" viewBox="0 0 60 42" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M4 34 L8 10 L20 22 L30 4 L40 22 L52 10 L56 34 Z" fill="#ffc21a" stroke="#7a3b00" stroke-width="2.5" stroke-linejoin="round"/>'
    '<rect x="4" y="33" width="52" height="7" rx="2" fill="#ffb300" stroke="#7a3b00" stroke-width="2.5"/>'
    '<circle cx="8" cy="9" r="3.5" fill="#d7263d"/><circle cx="30" cy="4" r="3.5" fill="#d7263d"/><circle cx="52" cy="9" r="3.5" fill="#d7263d"/>'
    '</svg>'
)


POINT_DOWN_SVG = (
    '<svg class="ico" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="12" cy="12" r="11" fill="#d7263d"/>'
    '<path d="M12 5 V16 M7 12 L12 17 L17 12" stroke="#fff" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)


def parse_post_date(value):
    """'21/10/2026', '21-10-2026' किंवा '2026-10-21' → date. ओळखता न आल्यास आजची तारीख (IST)."""
    text = str(value or "").strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return dt.datetime.strptime(text[:10], fmt).date()
        except ValueError:
            pass
    return (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date()


def load_content(path=None):
    with open(path or HERE / "content.json", "r", encoding="utf-8") as f:
        return json.load(f)


def pick_cta(date, content):
    """डिफॉल्ट: त्या वाराचा प्रश्न. rotation_enabled=true असल्यास दिवसाआड जास्तीच्या 10 पैकी एक
    (तारखेवरून ठरतो — त्याच तारखेला पुन्हा बनवले तरी तोच प्रश्न)."""
    primary = content["primary_cta"][WEEKDAYS[date.weekday()]]
    extra = content.get("rotating_cta") or []
    if content.get("rotation_enabled") and extra and date.toordinal() % 2 == 1:
        return extra[(date.toordinal() // 2) % len(extra)]
    return primary


def _max_price(r):
    try:
        return float(r.get("MaxPrice", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _price(value):
    try:
        return f"₹{int(float(value or 0)):,}"
    except (TypeError, ValueError):
        return "₹0"


def _box(id_, cls, inner_html, top=None, minsize=22):
    style = f' style="top:{top}px"' if top is not None else ""
    return f'<div id="{id_}" class="text {cls}" data-min="{minsize}"{style}><span>{inner_html}</span></div>'


def build_html(post_date, all_records, content=None):
    content = content or load_content()
    date = parse_post_date(post_date)
    top_5 = sorted(all_records, key=_max_price, reverse=True)[:5]
    day = WEEKDAYS_MR[date.weekday()]

    layers = [
        _box("date", "", date.strftime("%d-%m-%Y"), minsize=39),
        _box("day", "wrap", f'{html.escape(day)}<br><b>{html.escape(content.get("badge_suffix", "स्पेशल"))}</b>', minsize=24),
    ]
    if content.get("show_weekday_title_on_image"):
        layers.append(_box("wtitle", "", html.escape(content["weekday_titles"][WEEKDAYS[date.weekday()]]), minsize=22))
    for i, r in enumerate(top_5):
        top = ROW_TOPS[i]
        first = " first" if i == 0 else ""
        district = str(r.get("District", "") or "").strip()
        layers += [
            _box(f"rank-{i+1}", "rank" + first, f"{i+1:02}", top),
            _box(f"market-{i+1}", "market" + first, html.escape(str(r.get("Market", "-"))), top + 8, 18),
            _box(f"district-{i+1}", "district" + first, html.escape(("जिल्हा " + district) if district else ""), top + 54, 17),
            _box(f"price-{i+1}", "price" + first, _price(r.get("MaxPrice", 0)), top + 3, 30),
            _box(f"unit-{i+1}", "unit" + first, "प्रति क्विंटल", top + 61, 17),
        ]
    cta = pick_cta(date, content)
    # इमोजी GitHub सर्व्हरवर फॉन्टवर अवलंबून न राहता कायमच्या चिन्हाने (SVG) दाखवा
    cta_html = html.escape(EMOJI_RE.sub("", cta).strip())
    if "👇" in cta:
        cta_html += " " + POINT_DOWN_SVG
    layers.append(_box("cta", "wrap", cta_html, minsize=24))

    page = (HERE / "template.html").read_text(encoding="utf-8")
    page = page.replace("__FONT__", base64.b64encode((HERE / "fonts/NotoSansDevanagari.ttf").read_bytes()).decode())
    page = page.replace("__BACKGROUND__", base64.b64encode((HERE / "static_background.png").read_bytes()).decode())
    page = page.replace("__CROWN__", CROWN_SVG if top_5 else "")
    return page.replace("__TEXT_LAYERS__", "\n".join(layers)), {"date": str(date), "day": day, "cta": cta, "rows": len(top_5)}


def generate_mh_cover(post_date, all_records, output_path, browser=None):
    """playwright ने 1080x1350 PNG बनवतो. browser दिला नसेल तर स्वतः उघडतो."""
    from playwright.sync_api import sync_playwright

    page_html, info = build_html(post_date, all_records)

    def shoot(b):
        page = b.new_page(viewport={"width": 1080, "height": 1350})
        page.set_content(page_html, wait_until="load")
        report = page.evaluate("window.__fit()")
        page.wait_for_timeout(200)
        page.screenshot(path=output_path, full_page=False)
        page.close()
        return report

    if browser is not None:
        report = shoot(browser)
    else:
        with sync_playwright() as p:
            b = p.chromium.launch()
            try:
                report = shoot(b)
            finally:
                b.close()
    if report.get("problems"):
        print("⚠️ महाराष्ट्र कव्हर: काही मजकूर जागेत पूर्ण बसला नाही:", report["problems"])
    print(f"✅ महाराष्ट्र नवीन कव्हर: {info['date']} {info['day']} | प्रश्न: {info['cta']}")
    return report
