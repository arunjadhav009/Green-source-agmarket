"""Agmarknet (data.gov.in) वरून सर्व राज्यांचे कांदा भाव घेणे आणि राज्यवार पोस्टचे गट बनवणे.
(पूर्वी n8n चे 'Agmarknet Daily Onion Data Extract' + 'Process States Separately')

fetch_records()  -> data.gov.in API मधून Onion च्या सर्व नोंदी
build_groups()   -> सर्वात नवीन तारखेचा डेटा, राज्यवार पाने (18 ओळी/पान)
                    महाराष्ट्र नेहमी पहिला, नंतर जास्त डेटा ते कमी;
                    10 पेक्षा कमी नोंदी असलेली राज्ये (महाराष्ट्र सोडून) एकाच शेवटच्या अल्बममध्ये
save_csv()       -> data/agmarket/YYYY-MM-DD.csv
"""
import csv
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
PROXY_URL = "https://api.ajreelsmedia.in/"
PAGE_SIZE = 18
SMALL_STATE_LIMIT = 10
IST = timezone(timedelta(hours=5, minutes=30))


def _mask(value):
    if value and os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::add-mask::{value}", flush=True)


def fetch_records():
    key = os.environ.get("DATA_GOV_API_KEY", "").strip()
    if not key:
        print("❌ DATA_GOV_API_KEY secret सापडला नाही (Settings → Secrets and variables → Actions).")
        sys.exit(1)
    _mask(key)
    last = ""
    for attempt in range(1, 4):
        try:
            if attempt < 3:   # GitHub ला data.gov.in थेट मिळत नाही → Hostinger वरचा proxy (api.ajreelsmedia.in)
                r = requests.get(PROXY_URL, params={"limit": 9000, "offset": 0},
                                 headers={"X-Api-Key": key}, timeout=180)
            else:             # शेवटचा प्रयत्न थेट data.gov.in ला
                r = requests.get(API_URL, params={"api-key": key, "format": "json", "filters[commodity]": "Onion",
                                                  "limit": 9000, "offset": 0}, timeout=90)
            j = r.json()
            recs = [x for x in (j.get("records") or []) if x.get("commodity") == "Onion"]
            if recs:
                print(f"Agmarknet: {len(recs)} नोंदी मिळाल्या")
                return recs
            last = j.get("message") or j.get("error") or f"रिकामा डेटा (HTTP {r.status_code})"
        except Exception as e:
            last = type(e).__name__   # URL मध्ये key असते, म्हणून पूर्ण error छापत नाही
        print(f"⚠️ data.gov.in प्रयत्न {attempt}/3 अयशस्वी: {last}")
        time.sleep(5)
    print("❌ data.gov.in वरून डेटा मिळाला नाही.")
    sys.exit(1)


def _num(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _date_key(d):
    try:
        dd, mm, yy = [int(x) for x in str(d).replace("-", "/").split("/")]
        return yy * 10000 + mm * 100 + dd
    except ValueError:
        return 0


def latest_records(records):
    dates = [str(r.get("arrival_date") or "").strip() for r in records]
    dates = [d for d in dates if d]
    if not dates:
        print("❌ डेटामध्ये तारीख नाही.")
        sys.exit(1)
    latest = max(dates, key=_date_key)
    return latest, [r for r in records if str(r.get("arrival_date") or "").strip() == latest]


def build_groups(records):
    post_date, rows = latest_records(records)
    states = {}
    for r in rows:
        st = str(r.get("state") or "").strip()
        if not st:
            continue
        states.setdefault(st, []).append({
            "District": r.get("district") or "-",
            "Market": r.get("market") or "-",
            "MinPrice": _num(r.get("min_price")),
            "MaxPrice": _num(r.get("max_price")),
            "ModalPrice": _num(r.get("modal_price")),
        })

    normal, small_pages, small_names = [], [], []
    for name, recs in states.items():
        recs.sort(key=lambda x: x["MaxPrice"], reverse=True)
        is_mh = name.lower() == "maharashtra"
        if len(recs) < SMALL_STATE_LIMIT and not is_mh:
            small_names.append(name)
            small_pages.append({"StateName": name, "PostDate": post_date, "CurrentPage": 1, "TotalPages": 1,
                                "TotalRecords": len(recs), "PageData": recs})
        else:
            total = -(-len(recs) // PAGE_SIZE) or 1
            pages = [{"StateName": name, "PostDate": post_date, "CurrentPage": i + 1, "TotalPages": total,
                      "TotalRecords": len(recs), "PageData": recs[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]}
                     for i in range(total)]
            normal.append((name, len(recs), pages))

    normal.sort(key=lambda x: (x[0].lower() != "maharashtra", -x[1]))
    groups = [{"state": n, "pages": p} for n, _, p in normal]

    if small_pages:
        title = ", ".join(small_names)
        for i, p in enumerate(small_pages):
            p.update(CurrentPage=i + 1, TotalPages=len(small_pages), CombinedTitle=title)
        groups.append({"state": title, "pages": small_pages})

    print(f"तारीख {post_date}: {len(states)} राज्ये → {len(groups)} पोस्ट्स")
    return post_date, groups


def save_csv(records):
    day = datetime.now(IST).strftime("%Y-%m-%d")
    out = Path(__file__).resolve().parent / "data" / "agmarket" / f"{day}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = ["arrival_date", "state", "district", "market", "variety", "grade", "min_price", "max_price", "modal_price"]
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)
    print(f"डेटा सेव्ह: data/agmarket/{day}.csv")
