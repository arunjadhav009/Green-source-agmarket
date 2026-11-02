import os
import json
import requests

FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")


def get_page_token(token):
    # System User token असेल तर त्यातून Page token मिळवणे; आधीच Page token असेल तर तोच वापरणे
    if not token or not FB_PAGE_ID:
        return token
    try:
        res = requests.get(
            f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}",
            params={"fields": "access_token", "access_token": token},
            timeout=30,
        ).json()
        return res.get("access_token") or token
    except Exception:
        return token


FB_PAGE_ACCESS_TOKEN = get_page_token(FB_PAGE_ACCESS_TOKEN)

def main():
    if not FB_PAGE_ID or not FB_PAGE_ACCESS_TOKEN:
        print("❌ Facebook क्रेडेंशियल्स उपलब्ध नाहीत.")
        return

    meta_path = "output_images/meta.json"
    if not os.path.exists(meta_path):
        print("❌ इमेजेस सापडल्या नाहीत.")
        return

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    state_name = meta.get("state_name")
    caption = meta.get("caption")
    total = meta.get("total_pages")

    fb_photo_ids = []
    for idx in range(1, total + 1):
        img_path = f"output_images/page_{idx}.png"
        url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/photos"
        with open(img_path, "rb") as f:
            res = requests.post(
                url,
                data={"access_token": FB_PAGE_ACCESS_TOKEN, "published": "false"},
                files={"source": f}
            ).json()

        if "id" in res:
            fb_photo_ids.append(res["id"])
            print(f"✅ FB Image {idx}/{total} Uploaded (ID: {res['id']})")
        else:
            print(f"❌ FB Upload Failed (Page {idx}): {res}")

    if not fb_photo_ids:
        print("❌ एकही इमेज फेसबुकवर अपलोड झाली नाही.")
        return

    print(f"🚀 Facebook वर {state_name} ची अखंड पोस्ट पब्लिश होत आहे...")
    feed_url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/feed"
    payload = {
        "message": caption,
        "attached_media": json.dumps([{"media_fbid": pid} for pid in fb_photo_ids]),
        "access_token": FB_PAGE_ACCESS_TOKEN
    }
    resp = requests.post(feed_url, data=payload).json()
    print("✅ Facebook Response:", resp)

if __name__ == "__main__":
    main()
