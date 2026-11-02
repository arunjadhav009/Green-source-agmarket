# Green Source — Agmarket (All India) कांदा भाव automation

n8n शिवाय, पूर्णपणे GitHub Actions वर.

| Workflow | काय करतो | कधी |
|---|---|---|
| `Agmarket All India Daily Posts (FB + Insta)` | data.gov.in (Agmarknet) वरून सर्व राज्यांचे कांदा भाव → राज्यवार Top 5 कव्हर + भावांची पाने → FB + Insta, 5-5 मिनिटांनी | रोज 7:15 PM (IST) पासून |

- महाराष्ट्र नेहमी पहिला, नंतर जास्त डेटा असलेली राज्ये. 10 पेक्षा कमी नोंदी असलेली राज्ये शेवटी एकाच अल्बममध्ये.
- कमेंट auto-reply **Green-source-Msamb** repo मधून होतो (त्याच page साठी एकच reply सिस्टीम). तो `#GreenSourceMandiBhav` वरून राज्याची पोस्ट ओळखतो.

## Secrets (Settings → Secrets and variables → Actions)
- `FB_TOKEN` — Facebook token
- `DATA_GOV_API_KEY` — data.gov.in API key

दोन्ही कधीही code मध्ये लिहायचे नाहीत. Logs मध्ये ते `***` दिसतात.

## चालू / बंद
- Variable `LIVE = true` → रोजचं schedule चालू. नसेल तर फक्त हाताने "Run workflow".
- हाताने चालवताना `no` = test mode (फक्त images, काहीही पोस्ट नाही). `only_states` मध्ये राज्यांची नावं देऊन फक्त तीच चालवता येतात.

## फाइल्स
- `run_all.py` — सगळ्या राज्यांची क्रमवार पोस्ट
- `agmarket_fetch.py` — data.gov.in डेटा, राज्यवार गट
- `generate_images.py`, `template.html`, `cover_template.html`, `mh_cover/`, `state_cover/` — images
- `post_facebook.py`, `post_instagram.py` — पोस्टिंग
- `data/agmarket/` — रोजचा डेटा (CSV)
