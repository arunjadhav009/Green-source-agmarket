import os
import json
import hashlib
import html
from playwright.sync_api import sync_playwright

PAGES_JSON = os.environ.get("PAGES_JSON")

STATE_THEMES = {
    "Maharashtra": {"primary": "#ff6f00", "secondary": "#e65100", "bg": "#fff8e1"},
    "Gujarat": {"primary": "#005a9c", "secondary": "#1976d2", "bg": "#f0f7ff"},
    "Karnataka": {"primary": "#311b92", "secondary": "#512da8", "bg": "#f4f1fa"},
    "Madhya Pradesh": {"primary": "#b71c1c", "secondary": "#c62828", "bg": "#fff5f5"},
    "Rajasthan": {"primary": "#bf360c", "secondary": "#d84315", "bg": "#fff8f5"},
    "Andhra Pradesh": {"primary": "#1b5e20", "secondary": "#2e7d32", "bg": "#f1f8f3"},
    "Telangana": {"primary": "#00695c", "secondary": "#00897b", "bg": "#f0fdfa"},
    "Uttar Pradesh": {"primary": "#4a148c", "secondary": "#6a1b9a", "bg": "#faf5ff"},
    "Punjab": {"primary": "#c2410c", "secondary": "#ea580c", "bg": "#fff7ed"},
    "Haryana": {"primary": "#0369a1", "secondary": "#0284c7", "bg": "#f0f9ff"},
    "West Bengal": {"primary": "#1e3a8a", "secondary": "#1d4ed8", "bg": "#eff6ff"},
    "Bihar": {"primary": "#831843", "secondary": "#9d174d", "bg": "#fdf2f8"},
    "Odisha": {"primary": "#0f766e", "secondary": "#14b8a6", "bg": "#f0fdfa"},
    "Tamil Nadu": {"primary": "#701a75", "secondary": "#86198f", "bg": "#fdf4ff"},
    "Kerala": {"primary": "#14532d", "secondary": "#166534", "bg": "#f0f4f4"},
    "Assam": {"primary": "#065f46", "secondary": "#059669", "bg": "#ecfdf5"},
    "Chhattisgarh": {"primary": "#854d0e", "secondary": "#a16207", "bg": "#fefce8"},
    "Jharkhand": {"primary": "#374151", "secondary": "#4b5563", "bg": "#f9fafb"},
    "Himachal Pradesh": {"primary": "#0e7490", "secondary": "#0891b2", "bg": "#ecfeff"},
    "Uttarakhand": {"primary": "#155e75", "secondary": "#0e7490", "bg": "#f0fdfa"},
    "Goa": {"primary": "#0284c7", "secondary": "#38bdf8", "bg": "#f0f9ff"},
    "Jammu and Kashmir": {"primary": "#334155", "secondary": "#475569", "bg": "#f8fafc"}
}

FALLBACK_PALETTES = [
    {"primary": "#1b5e20", "secondary": "#2e7d32", "bg": "#f1f8f3"},
    {"primary": "#005a9c", "secondary": "#1976d2", "bg": "#f0f7ff"},
    {"primary": "#311b92", "secondary": "#512da8", "bg": "#f4f1fa"},
    {"primary": "#b71c1c", "secondary": "#c62828", "bg": "#fff5f5"},
    {"primary": "#bf360c", "secondary": "#d84315", "bg": "#fff8f5"},
    {"primary": "#00695c", "secondary": "#00897b", "bg": "#f0fdfa"},
    {"primary": "#4a148c", "secondary": "#6a1b9a", "bg": "#faf5ff"}
]

LOCAL_TITLES = {
    "Madhya Pradesh": "मध्य प्रदेश प्याज मंडी भाव",
    "Maharashtra": "महाराष्ट्र कांदा बाजार भाव",
    "Gujarat": "गुजरात प्याज मंडी भाव",
    "Rajasthan": "राजस्थान प्याज मंडी भाव",
    "Uttar Pradesh": "उत्तर प्रदेश प्याज मंडी भाव",
    "Tamil Nadu": "Tamil Nadu Onion Rates",
    "Karnataka": "Karnataka Onion Rates",
    "Andhra Pradesh": "Andhra Pradesh Onion Rates",
    "Telangana": "Telangana Onion Rates",
    "Punjab": "पंजाब प्याज मंडी भाव",
    "Haryana": "हरियाणा प्याज मंडी भाव",
    "Bihar": "बिहार प्याज मंडी भाव",
    "Chhattisgarh": "छत्तीसगढ़ प्याज मंडी भाव",
    "Jharkhand": "झारखंड प्याज मंडी भाव",
    "Uttarakhand": "उत्तराखंड प्याज मंडी भाव",
    "Himachal Pradesh": "हिमाचल प्रदेश प्याज मंडी भाव",
    "Delhi": "दिल्ली प्याज मंडी भाव"
}

def get_state_theme(state_name):
    for key, val in STATE_THEMES.items():
        if key.lower() in state_name.lower() or state_name.lower() in key.lower():
            return val
    idx = int(hashlib.md5(state_name.encode()).hexdigest(), 16) % len(FALLBACK_PALETTES)
    return FALLBACK_PALETTES[idx]

HINDI_STATES = ["Gujarat", "Madhya Pradesh", "Rajasthan", "Uttar Pradesh", "Bihar", "Haryana",
                "Chhattisgarh", "Jharkhand", "Uttarakhand", "Himachal Pradesh", "Delhi", "Punjab"]

# कव्हर इमेज आणि caption मधला मजकूर, भाषेनुसार (mr = मराठी, hi = हिंदी, en = English)
LANG_TEXT = {
    "mr": {
        "subtitle": "आजचे टॉप 5 सर्वाधिक भाव",
        "district": "जिल्हा",
        "timing": "⏰ रोज संध्या. 7:30 ते 8:30",
        "ask": "💬 तुमच्या मार्केटचं नाव आणि आजचा भाव कमेंट करा!",
        "hint": "उदा. लासलगाव – ₹2,450",
        "unit": "₹ प्रति क्विंटल · कमाल भाव",
        "next": "सर्व भाव पुढील फोटोमध्ये",
    },
    "hi": {
        "subtitle": "आज के टॉप 5 अधिकतम भाव",
        "district": "जिला",
        "timing": "⏰ रोज़ शाम 7:30 से 8:30",
        "ask": "💬 आपकी मंडी का नाम और आज का भाव कमेंट करें!",
        "hint": "जैसे: नीमच – ₹2,450",
        "unit": "₹ प्रति क्विंटल · अधिकतम भाव",
        "next": "सभी भाव अगली फोटो में",
    },
    "en": {
        "subtitle": "Today's top 5 highest rates",
        "district": "",
        "timing": "⏰ Daily 7:30 – 8:30 PM",
        "ask": "💬 Comment your market name & today's rate!",
        "hint": "e.g. Kumbakonam – ₹2,450",
        "unit": "₹ per quintal · max price",
        "next": "All mandi rates in next photos",
    },
}


def get_state_lang(state_name):
    name = state_name.lower()
    if "maharashtra" in name:
        return "mr"
    if any(s.lower() == name for s in HINDI_STATES):
        return "hi"
    return "en"


def format_price(value):
    try:
        return f"₹{int(float(value or 0)):,}"
    except (TypeError, ValueError):
        return "₹0"


def generate_cover_image(state_name, post_date, all_records, output_path):
    with open("cover_template.html", "r", encoding="utf-8") as f:
        html_template = f.read()

    lang = get_state_lang(state_name)
    t = LANG_TEXT[lang]

    # कमाल भावानुसार पहिल्या ५ मार्केटची निवड करणे
    def max_price(r):
        try:
            return float(r.get("MaxPrice", 0) or 0)
        except (TypeError, ValueError):
            return 0.0

    top_5 = sorted(all_records, key=max_price, reverse=True)[:5]

    state_title = LOCAL_TITLES.get(state_name, f"{state_name} Onion Rates")

    cards_html = ""
    for idx, r in enumerate(top_5):
        market = html.escape(str(r.get("Market", "-")))
        district = html.escape(str(r.get("District", "-")))
        district_line = f"{t['district']} {district}".strip()
        # एकत्रित छोट्या राज्यांच्या पोस्टमध्ये मार्केट कोणत्या राज्याचं ते दाखवणे
        if r.get("_State"):
            district_line += f" · {html.escape(str(r['_State']))}"
        first_cls = " first" if idx == 0 else ""
        cards_html += f"""
        <div class="card{first_cls}">
          <div class="rank">{idx + 1:02d}</div>
          <div class="info">
            <div class="market">{market}</div>
            <div class="district">{district_line}</div>
          </div>
          <div class="price">{format_price(r.get('MaxPrice', 0))}</div>
        </div>
        """

    rendered = (
        html_template.replace("{{LANG}}", lang)
        .replace("{{POST_DATE}}", html.escape(str(post_date).replace("/", "-")))
        .replace("{{STATE_TITLE}}", html.escape(state_title))
        .replace("{{TOP_SUBTITLE}}", t["subtitle"])
        .replace("{{TOP_CARDS_HTML}}", cards_html)
        .replace("{{TIMING}}", t["timing"])
        .replace("{{ASK_LINE}}", t["ask"])
        .replace("{{ASK_HINT}}", html.escape(t["hint"]))
        .replace("{{FOOTER_UNIT}}", t["unit"])
        .replace("{{FOOTER_NEXT}}", t["next"])
    )

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.set_content(rendered, wait_until="load")
        page.wait_for_timeout(300)
        page.screenshot(path=output_path, full_page=False)
        browser.close()


def build_caption(state_name, post_date):
    lang = get_state_lang(state_name)
    tag = "#" + "".join(ch for ch in state_name.title() if ch.isalnum())
    if lang == "mr":
        body = (
            f"🧅 {state_name} कांदा बाजार भाव ({post_date})\n\n"
            "⏰ रोज संध्याकाळी 7:30 ते 8:30 दरम्यान ताजे बाजार भाव इथे मिळतील. पेज फॉलो करा 🔔\n\n"
            "💬 तुमच्या मार्केटमध्ये आज काय भाव निघाला? मार्केटचं नाव आणि भाव खाली कमेंट करा 👇\n\n"
            "👍 लाईक करा आणि शेतकरी मित्रांसोबत शेअर करा.\n"
        )
    elif lang == "hi":
        body = (
            f"🧅 {state_name} प्याज मंडी भाव ({post_date})\n\n"
            "⏰ रोज़ शाम 7:30 से 8:30 के बीच ताज़ा मंडी भाव यहाँ मिलेंगे। पेज फॉलो करें 🔔\n\n"
            "💬 आपकी मंडी में आज क्या भाव रहा? मंडी का नाम और भाव नीचे कमेंट करें 👇\n\n"
            "👍 लाइक करें और किसान साथियों के साथ शेयर करें।\n"
        )
    else:
        body = (
            f"🧅 {state_name} Onion Mandi Rates ({post_date})\n\n"
            "⏰ Fresh mandi rates every day between 7:30 and 8:30 PM. Follow the page 🔔\n\n"
            "💬 What was the rate in your market today? Comment your market name and rate 👇\n\n"
            "👍 Like and share with your farmer friends.\n"
        )
    # #GreenSourceMandiBhav हा ठरलेला शब्द n8n कमेंट रिप्लायमध्ये राज्याची पोस्ट ओळखण्यासाठी वापरला जातो
    return body + f"#GreenSourceMandiBhav #OnionRate #MandiBhav {tag}"


def generate_data_image(page_data, current_page, total_pages, output_path):
    with open("template.html", "r", encoding="utf-8") as f:
        html_template = f.read()

    state_name = str(page_data.get("StateName", "State"))
    theme = get_state_theme(state_name)

    rows_html = ""
    for r in page_data.get("PageData", []):
        rows_html += f"""
        <tr>
            <td>{r.get('District', '-')}</td>
            <td>{r.get('Market', '-')}</td>
            <td>₹{r.get('MinPrice', 0)}</td>
            <td>₹{r.get('MaxPrice', 0)}</td>
            <td class="modal-price">₹{r.get('ModalPrice', 0)}</td>
        </tr>
        """

    rendered = (
        html_template.replace("{{STATE_NAME}}", state_name)
        .replace("{{POST_DATE}}", str(page_data.get("PostDate", "")))
        .replace("{{CURRENT_PAGE}}", str(current_page))
        .replace("{{TOTAL_PAGES}}", str(total_pages))
        .replace("{{TABLE_ROWS}}", rows_html)
        .replace("{{PRIMARY_COLOR}}", theme["primary"])
        .replace("{{SECONDARY_COLOR}}", theme["secondary"])
        .replace("{{BG_COLOR}}", theme["bg"])
    )

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.set_content(rendered)
        page.screenshot(path=output_path, full_page=False)
        browser.close()

def main():
    if not PAGES_JSON or str(PAGES_JSON).strip() in ("", "None", "null"):
        print("❌ PAGES_JSON रिकामा आहे.")
        return

    data = PAGES_JSON
    for _ in range(5):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception as e:
                break
        else:
            break

    pages = []
    if isinstance(data, list):
        pages = data
    elif isinstance(data, dict):
        if "pages" in data and isinstance(data["pages"], list):
            pages = data["pages"]
        elif "PageData" in data:
            pages = [data]
        else:
            pages = list(data.values()) if data else []

    if not pages:
        print("❌ कोणताही पेज डेटा सापडला नाही.")
        return

    os.makedirs("output_images", exist_ok=True)

    combined_title = pages[0].get("CombinedTitle")
    post_date = pages[0].get("PostDate", "")
    state_name = combined_title or pages[0].get("StateName", "All India")

    # सर्व पेजेसचा एकत्रित डेटा टॉप ५ शोधण्यासाठी गोळा करणे
    all_records = []
    for p in pages:
        for rec in p.get("PageData", []):
            if combined_title:
                rec = dict(rec, _State=p.get("StateName", ""))
            all_records.append(rec)

    caption = build_caption(state_name, post_date)

    total_slides = len(pages) + 1  # १ कव्हर + डेटा पेजेस

    with open("output_images/meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "state_name": state_name,
            "caption": caption,
            "total_pages": total_slides
        }, f, ensure_ascii=False)

    print(f"🎬 १. Top 5 कव्हर पोस्टर तयार होत आहे: {state_name}...")
    cover_out = "output_images/page_1.png"
    generate_cover_image(state_name, post_date, all_records, cover_out)
    print("✅ Page 1 (Top 5 Cover) तयार झाले!")

    print(f"📊 २. उर्वरित {len(pages)} डेटा पेजेस तयार होत आहेत...")
    for idx, page in enumerate(pages):
        out_file = f"output_images/page_{idx + 2}.png"
        generate_data_image(page, idx + 1, len(pages), out_file)
        print(f"✅ Data Slide {idx + 1} तयार झाली: {out_file}")

# ===== नवीन कव्हर डिझाइन (फक्त page_1) =====
# महाराष्ट्र → mh_cover (मराठी), मिक्स पोस्ट → state_cover (हिंदी),
# हिंदी राज्ये → state_cover (हिंदी), बाकी राज्ये → state_cover (English).
# नवीन कव्हरमध्ये काही चूक आली तर जुनेच कव्हर तयार होते, पोस्ट थांबत नाही.
import sys as _sys
_HERE = os.path.dirname(os.path.abspath(__file__))
for _d in ("mh_cover", "state_cover"):
    _sys.path.insert(0, os.path.join(_HERE, _d))

_old_generate_cover_image = generate_cover_image

def generate_cover_image(state_name, post_date, all_records, output_path):
    try:
        if any(r.get("_State") for r in all_records):
            from state_cover import generate_mix_cover
            generate_mix_cover(post_date, all_records, output_path)
            return
        lang = get_state_lang(state_name)
        if lang == "mr" and state_name.strip().lower() == "maharashtra":
            from mh_cover import generate_mh_cover
            generate_mh_cover(post_date, all_records, output_path)
            return
        if lang in ("hi", "en"):
            from state_cover import generate_state_cover
            generate_state_cover(state_name, post_date, all_records, output_path, lang)
            return
    except Exception as e:
        print(f"⚠️ नवीन कव्हर तयार झाले नाही, जुने कव्हर वापरत आहे: {e}")
    _old_generate_cover_image(state_name, post_date, all_records, output_path)

if __name__ == "__main__":
    main()
