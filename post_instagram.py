import os
import json
import time
import requests

FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.environ.get("IG_ACCOUNT_ID")


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

def get_photo_url(photo_id):
    """फेसबुकवरून फोटोची वैध URL मिळवण्यासाठी रीट्राय लॉजिक"""
    url = f"https://graph.facebook.com/v20.0/{photo_id}"
    params = {
        "access_token": FB_PAGE_ACCESS_TOKEN,
        "fields": "source,images"
    }
    for attempt in range(1, 11):
        try:
            res = requests.get(url, params=params).json()
            if "images" in res and len(res["images"]) > 0:
                return res["images"][0]["source"]
            if "source" in res and res["source"]:
                return res["source"]
        except Exception as e:
            print(f"⚠️ URL मिळवताना एरर (प्रयत्न {attempt}): {e}")
        time.sleep(4)
    return ""

def wait_for_container(creation_id, max_attempts=15):
    """कंटेनर पूर्णपणे प्रक्रिया (FINISHED) होईपर्यंत वाट पाहणे"""
    status_url = f"https://graph.facebook.com/v20.0/{creation_id}"
    params = {
        "access_token": FB_PAGE_ACCESS_TOKEN,
        "fields": "status_code"
    }
    for _ in range(max_attempts):
        try:
            res = requests.get(status_url, params=params).json()
            status = res.get("status_code")
            if status == "FINISHED":
                return True
            if status == "ERROR":
                print(f"❌ Container Error ({creation_id}):", res)
                return False
        except Exception:
            pass
        time.sleep(4)
    return True

def publish_carousel(urls, caption_text):
    """१० किंवा त्यापेक्षा कमी इमेजेसचा कॅरोसेल सुरक्षितपणे पोस्ट करणे"""
    if len(urls) == 1:
        con = requests.post(
            f"https://graph.facebook.com/v20.0/{IG_ACCOUNT_ID}/media",
            data={"access_token": FB_PAGE_ACCESS_TOKEN, "image_url": urls[0], "caption": caption_text}
        ).json()
        if "id" in con:
            wait_for_container(con["id"], max_attempts=12)
            time.sleep(3)
            pub = requests.post(
                f"https://graph.facebook.com/v20.0/{IG_ACCOUNT_ID}/media_publish",
                data={"access_token": FB_PAGE_ACCESS_TOKEN, "creation_id": con["id"]}
            ).json()
            print("✅ Instagram Single Post Published:", pub)
        return

    child_ids = []
    for idx, u in enumerate(urls):
        ch = requests.post(
            f"https://graph.facebook.com/v20.0/{IG_ACCOUNT_ID}/media",
            data={"access_token": FB_PAGE_ACCESS_TOKEN, "image_url": u, "is_carousel_item": "true"}
        ).json()
        if "id" in ch:
            child_id = ch["id"]
            # Pratyek child slide finish zalyachi khatri karne
            wait_for_container(child_id, max_attempts=10)
            child_ids.append(child_id)
            print(f"  ↳ Carousel Slide {idx + 1}/{len(urls)} Ready (ID: {child_id})")
        else:
            print(f"⚠️ Child container {idx + 1} अयशस्वी:", ch)
        time.sleep(2)

    if len(child_ids) == len(urls):
        print("⏳ सर्व स्लाइड्स तयार झाल्या. मुख्य कॅरोसेल कंटेनर बनवत आहे...")
        time.sleep(5)
        car = requests.post(
            f"https://graph.facebook.com/v20.0/{IG_ACCOUNT_ID}/media",
            data={
                "access_token": FB_PAGE_ACCESS_TOKEN,
                "media_type": "CAROUSEL",
                "caption": caption_text,
                "children": ",".join(child_ids)
            }
        ).json()

        if "id" in car:
            car_id = car["id"]
            print(f"⏳ कॅरोसेल कंटेनर ID: {car_id}. Instagram वर प्रक्रिया पूर्ण होण्याची वाट पाहत आहे...")
            wait_for_container(car_id, max_attempts=15)
            time.sleep(5)
            pub = requests.post(
                f"https://graph.facebook.com/v20.0/{IG_ACCOUNT_ID}/media_publish",
                data={"access_token": FB_PAGE_ACCESS_TOKEN, "creation_id": car_id}
            ).json()
            print("✅ Instagram Carousel Published:", pub)
        else:
            print("❌ Instagram Carousel निर्मिती अयशस्वी:", car)
    else:
        print("❌ सर्व स्लाइड्स तयार न झाल्यामुळे कॅरोसेल पोस्ट रद्द केली.")

def main():
    if not IG_ACCOUNT_ID or not FB_PAGE_ACCESS_TOKEN or not FB_PAGE_ID:
        print("❌ Instagram/Facebook क्रेडेंशियल्स उपलब्ध नाहीत.")
        return

    meta_path = "output_images/meta.json"
    if not os.path.exists(meta_path):
        print("❌ output_images/meta.json फाईल सापडली नाही.")
        return

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    caption = meta.get("caption", "")
    total = meta.get("total_pages", 0)

    if total == 0:
        print("❌ एकही पेज सापडले नाही.")
        return

    media_urls = []
    print(f"🚀 Instagram साठी {total} इमेजेस फेसबुकवर अपलोड करून लिंक्स गोळा करत आहे...")

    for idx in range(1, total + 1):
        img_path = f"output_images/page_{idx}.png"
        if not os.path.exists(img_path):
            continue

        upload_url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/photos"
        with open(img_path, "rb") as f:
            res = requests.post(
                upload_url,
                data={"access_token": FB_PAGE_ACCESS_TOKEN, "published": "false"},
                files={"source": f}
            ).json()

        if "id" in res:
            p_url = get_photo_url(res["id"])
            if p_url:
                media_urls.append(p_url)
                print(f"✅ Image {idx}/{total} ची URL मिळाली.")
        time.sleep(1)

    if not media_urls:
        print("❌ एकही वैध URL मिळाली नाही.")
        return

    batch_size = 10
    total_batches = (len(media_urls) + batch_size - 1) // batch_size

    for batch_idx in range(total_batches):
        batch_urls = media_urls[batch_idx * batch_size : (batch_idx + 1) * batch_size]
        
        if total_batches > 1:
            batch_caption = f"{caption}\n\n📌 (Part {batch_idx + 1} of {total_batches})"
        else:
            batch_caption = caption

        print(f"\n📦 बॅच {batch_idx + 1}/{total_batches} ({len(batch_urls)} इमेजेस) Instagram वर पोस्ट होत आहे...")
        publish_carousel(batch_urls, batch_caption)

        if batch_idx + 1 < total_batches:
            print("⏳ पुढील बॅचसाठी १५ सेकंद थांबत आहे...")
            time.sleep(15)

if __name__ == "__main__":
    main()
