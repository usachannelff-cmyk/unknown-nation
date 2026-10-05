import json, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEEDS = [
    ("World", "BBC", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("India", "Google News", "https://news.google.com/rss/search?q=India&hl=en-IN&gl=IN&ceid=IN:en"),
    ("Technology", "Google News", "https://news.google.com/rss/search?q=technology&hl=en&gl=US&ceid=US:en"),
    ("Gaming", "Google News", "https://news.google.com/rss/search?q=gaming&hl=en&gl=US&ceid=US:en"),
    ("Sports", "Google News", "https://news.google.com/rss/search?q=sports&hl=en&gl=US&ceid=US:en"),
]

def clean_text(value):
    return " ".join((value or "").split())

def get_items(category, source, url):
    req = urllib.request.Request(url, headers={"User-Agent":"UNKNOWN-News-Bot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    root = ET.fromstring(data)
    out=[]
    for item in root.findall(".//item")[:10]:
        title=clean_text(item.findtext("title"))
        link=clean_text(item.findtext("link"))
        pub=clean_text(item.findtext("pubDate"))
        if not title or not link:
            continue
        try:
            dt=parsedate_to_datetime(pub).astimezone(timezone.utc)
            published=dt.strftime("%Y-%m-%d %H:%M UTC")
            sort_time=dt.timestamp()
        except Exception:
            published=pub or "Latest"
            sort_time=0
        out.append({
            "category": category,
            "source": source,
            "title": title,
            "link": link,
            "published": published,
            "_sort": sort_time
        })
    return out

news=[]
for category, source, url in FEEDS:
    try:
        news.extend(get_items(category, source, url))
    except Exception as e:
        print(f"Feed failed: {source} / {category}: {e}")

# Newest first, remove duplicate title+link pairs, keep max 50.
seen=set()
unique=[]
for item in sorted(news, key=lambda x:x["_sort"], reverse=True):
    key=(item["title"].lower(), item["link"])
    if key in seen: continue
    seen.add(key)
    item.pop("_sort", None)
    unique.append(item)
    if len(unique)>=50: break

with open("news.json","w",encoding="utf-8") as f:
    json.dump(unique,f,ensure_ascii=False,indent=2)

print(f"Wrote {len(unique)} headlines.")
