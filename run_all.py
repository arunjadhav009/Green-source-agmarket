"""सर्व राज्यांच्या पोस्ट्स एकामागून एक (पूर्वी n8n चा 'Loop Over States' + 'Wait 5 Minutes').

प्रत्येक राज्यासाठी: images बनवणे (generate_images.py) → Facebook (post_facebook.py) → Instagram (post_instagram.py)
दोन पोस्ट्समध्ये GAP_MINUTES मिनिटांचं अंतर.
TEST MODE (DRY_RUN=true): फक्त images बनतात, काहीही पोस्ट होत नाही, थांबणंही नाही.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests

from agmarket_fetch import fetch_records, fetch_today_records, build_groups, save_csv

PAGE_ID = "609269705592123"
IG_ACCOUNT_ID = "17841412056274162"
GAP_MINUTES = 5

HERE = Path(__file__).resolve().parent
DRY_RUN = os.environ.get("DRY_RUN", "false").strip().lower() == "true"
ONLY = os.environ.get("ONLY_STATES", "").strip()   # हाताने चालवताना: फक्त ही राज्ये (comma ने)


def mask(value):
    if value and os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::add-mask::{value}", flush=True)


def page_token():
    token = os.environ.get("FB_TOKEN", "").strip()
    if not token:
        print("❌ FB_TOKEN secret सापडला नाही.")
        sys.exit(1)
    mask(token)
    try:
        res = requests.get(f"https://graph.facebook.com/{PAGE_ID}", params={"fields": "access_token"},
                           headers={"Authorization": f"Bearer {token}"}, timeout=30).json()
        if res.get("access_token"):
            mask(res["access_token"])
            return res["access_token"]
        if "error" in res:
            print("⚠️ Page token मिळाला नाही:", res["error"].get("message", ""))
    except Exception as e:
        print("⚠️ Page token मिळवताना अडचण:", type(e).__name__)
    return token


def run(script, env):
    r = subprocess.run([sys.executable, script], cwd=HERE, env=env)
    return r.returncode == 0


def main():
    # आजचा डेटा आला तरच पोस्ट: नसेल तर 5-5 मिनिटांनी 45 मिनिटांपर्यंत वाट पाहणे
    if DRY_RUN:
        records = fetch_records()
    else:
        records = fetch_today_records(wait_minutes=45, every_minutes=5)
        if records is None:
            print("❌ 45 मिनिटं थांबूनही आजचा Agmarknet डेटा आला नाही. जुना डेटा पोस्ट करणार नाही — आज पोस्ट नाही.")
            sys.exit(1)
    post_date, groups = build_groups(records, allow_old=DRY_RUN)
    if ONLY:
        wanted = [s.strip().lower() for s in ONLY.split(",") if s.strip()]
        groups = [g for g in groups if any(w in g["state"].lower() for w in wanted)]
        print(f"फक्त निवडलेली: {[g['state'] for g in groups]}")

    env = dict(os.environ)
    if not DRY_RUN:
        save_csv(records)
        env.update(FB_PAGE_ID=PAGE_ID, FB_PAGE_ACCESS_TOKEN=page_token(), IG_ACCOUNT_ID=IG_ACCOUNT_ID)
    env.pop("FB_TOKEN", None)

    keep = HERE / "all_images"
    shutil.rmtree(keep, ignore_errors=True)
    keep.mkdir()

    done = 0
    for i, g in enumerate(groups, 1):
        started = time.time()
        print(f"\n========== {i}/{len(groups)}: {g['state']} ({len(g['pages'])} पाने) ==========", flush=True)
        shutil.rmtree(HERE / "output_images", ignore_errors=True)
        env["PAGES_JSON"] = json.dumps(g["pages"], ensure_ascii=False)
        if not run("generate_images.py", env):
            print(f"❌ {g['state']}: images बनल्या नाहीत, पुढच्या राज्याकडे जात आहे.")
            continue
        safe = "".join(c if c.isalnum() else "_" for c in g["state"])[:40]
        for p in sorted((HERE / "output_images").glob("page_*.png")):
            shutil.copy(p, keep / f"{i:02d}_{safe}_{p.name}")

        if DRY_RUN:
            done += 1
            continue
        run("post_facebook.py", env)
        run("post_instagram.py", env)
        done += 1

        if i < len(groups):
            wait = GAP_MINUTES * 60 - (time.time() - started)
            if wait > 0:
                print(f"⏳ पुढच्या पोस्टसाठी {int(wait)} सेकंद थांबत आहे...", flush=True)
                time.sleep(wait)

    print(f"\n✅ {done}/{len(groups)} पोस्ट्स पूर्ण" + ("  [TEST MODE — काहीही पोस्ट केले नाही]" if DRY_RUN else ""))


if __name__ == "__main__":
    main()
