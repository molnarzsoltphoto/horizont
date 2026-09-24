import datetime as dt
import email.utils
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "news.json"
NOW = dt.datetime.now(dt.timezone.utc)
QUERIES = {
    "MÁV": '"MÁV" OR "MÁV-csoport" OR "MÁVINFORM" OR "Volánbusz" OR "HÉV"',
    "Magyar közlekedés": '"magyar közlekedés" OR "BKK" OR "autópálya" OR "közösségi közlekedés"',
    "Nemzetközi vasút": '"international rail" OR "European railways" OR "night trains" OR "high speed rail"',
    "Jégkorong": '"jégkorong" OR "hoki" OR "ice hockey"',
    "Csillagászat": '"csillagászat" OR "űrkutatás" OR "astronomy" OR "NASA"',
    "Belpolitika": '"magyar belpolitika" OR "kormány" OR "Országgyűlés"',
    "Külpolitika": '"külpolitika" OR "nemzetközi politika" OR "foreign policy"',
    "Gazdaság": '"magyar gazdaság" OR "infláció" OR "GDP" OR "gazdasági hírek"',
}
RSS_NS = {"media": "http://search.yahoo.com/mrss/", "content": "http://purl.org/rss/1.0/modules/content/"}
HEADERS = {"User-Agent": "HorizontRSSReader/1.0 (+personal news reader)", "Accept": "application/rss+xml, application/xml, text/xml"}

def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()

def image_for(entry):
    candidates = []
    for name in ("media:thumbnail", "media:content"):
        for element in entry.findall(name, RSS_NS):
            candidates.append(element.get("url", ""))
    for enclosure in entry.findall("enclosure"):
        if enclosure.get("type", "").startswith("image/"):
            candidates.append(enclosure.get("url", ""))
    for url in candidates:
        if url.startswith("https://"):
            return url
    return None

def load_existing():
    try:
        return json.loads(OUTPUT.read_text(encoding="utf-8")).get("articles", [])
    except (OSError, ValueError):
        return []

def main():
    previous = load_existing()
    fresh = []
    successful = 0
    for category, query in QUERIES.items():
        locale = "en-US&gl=US&ceid=US:en" if category == "Nemzetközi vasút" else "hu&gl=HU&ceid=HU:hu"
        language = locale.split("&", 1)[0]
        gl = "US" if language == "en-US" else "HU"
        ceid = "US:en" if gl == "US" else "HU:hu"
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": query + " when:7d", "hl": language, "gl": gl, "ceid": ceid})
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=18) as response:
                root = ET.fromstring(response.read(3_000_000))
            entries = root.findall("./channel/item")
            successful += 1
            for entry in entries[:45]:
                title = clean(entry.findtext("title"))
                link = (entry.findtext("link") or "").strip()
                parsed = urllib.parse.urlparse(link)
                if not title or parsed.scheme not in ("http", "https") or not parsed.netloc:
                    continue
                try:
                    published = email.utils.parsedate_to_datetime(entry.findtext("pubDate", ""))
                    if published.tzinfo is None:
                        published = published.replace(tzinfo=dt.timezone.utc)
                except (TypeError, ValueError):
                    continue
                if published < NOW - dt.timedelta(days=7) or published > NOW + dt.timedelta(days=1):
                    continue
                source_node = entry.find("source")
                source = clean(source_node.text if source_node is not None else "") or "Google Hírek"
                if title.endswith(" - " + source):
                    title = title[: -(len(source) + 3)]
                summary = clean(entry.findtext("description"))
                if summary == title or title in summary:
                    summary = ""
                fresh.append({"category": category, "title": title[:250], "url": link, "source": source[:100], "published": published.isoformat(), "summary": summary[:350], "image": image_for(entry)})
            print(f"{category}: {len(entries)} találat")
        except (OSError, ET.ParseError, ValueError) as error:
            print(f"{category}: hiba: {error}")
        time.sleep(0.3)
    if not successful:
        print("Nincs elérhető forrás, az előző adatok megmaradnak.")
        return
    by_url = {}
    for item in previous + fresh:
        if not isinstance(item, dict) or not item.get("url") or not item.get("title") or item.get("category") not in QUERIES:
            continue
        try:
            stamp = dt.datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=dt.timezone.utc)
            if stamp < NOW - dt.timedelta(days=7):
                continue
        except (ValueError, TypeError, KeyError):
            continue
        key = item["url"].split("?", 1)[0]
        if key not in by_url or (not by_url[key].get("image") and item.get("image")):
            by_url[key] = item
    items = sorted(by_url.values(), key=lambda x: x["published"], reverse=True)[:250]
    OUTPUT.write_text(json.dumps({"updated": NOW.isoformat(), "articles": items}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Összesen {len(items)} hír mentve.")

if __name__ == "__main__":
    main()
