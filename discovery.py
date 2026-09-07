import os, json, time, sqlite3, hashlib, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE=Path(__file__).resolve().parent
DB=BASE/"job_finder.db"
CONFIG=BASE/"search_config.json"
AGENTS={"User-Agent":"AutoApplyJobFinder/1.0 (personal job research)"}

def config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))

def connect():
    c=sqlite3.connect(DB,timeout=30)
    c.row_factory=sqlite3.Row
    c.execute("PRAGMA busy_timeout=30000")
    return c

def setup():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS discovery_jobs(
        id INTEGER PRIMARY KEY, fingerprint TEXT UNIQUE, company TEXT, title TEXT,
        location TEXT, url TEXT, description TEXT, source TEXT, posted_at TEXT,
        first_seen TEXT DEFAULT CURRENT_TIMESTAMP, status TEXT DEFAULT 'new')""")
        c.execute("""CREATE TABLE IF NOT EXISTS discovery_runs(
        id INTEGER PRIMARY KEY, started_at TEXT, finished_at TEXT, found INTEGER,
        inserted INTEGER, errors TEXT)""")

def fetch_json(url):
    req=urllib.request.Request(url,headers=AGENTS)
    with urllib.request.urlopen(req,timeout=35) as r:
        return json.load(r)

def strip_html(text):
    from html import unescape
    import re
    return unescape(re.sub(r"<[^>]+>"," ",text or "")).strip()

def greenhouse(board):
    data=fetch_json("https://boards-api.greenhouse.io/v1/boards/"+urllib.parse.quote(board,safe="")+"/jobs?content=true")
    for j in data.get("jobs",[]):
        yield dict(company=board,title=j.get("title",""),location=j.get("location",{}).get("name",""),
            url=j.get("absolute_url",""),description=strip_html(j.get("content","")),
            source="Greenhouse",posted_at=j.get("updated_at",""))

def lever(site):
    data=fetch_json("https://api.lever.co/v0/postings/"+urllib.parse.quote(site,safe="")+"?mode=json")
    for j in data:
        cats=j.get("categories") or {}
        yield dict(company=site,title=j.get("text",""),location=cats.get("location",""),
            url=j.get("hostedUrl",""),description=strip_html(j.get("descriptionPlain") or j.get("description","")),
            source="Lever",posted_at=j.get("createdAt",""))

def match(job,cfg):
    text=(job["title"]+" "+job["description"]).lower()
    title=job["title"].lower()
    if cfg.get("exclude_senior",True) and any(x in title for x in ["senior ","sr. ","staff ","principal ","director ","manager ","lead engineer","architect"]):
        return False
    if cfg.get("exclude_internships",False) and "intern" in title:
        return False
    terms=[x.lower() for x in cfg.get("title_keywords",[]) if x.strip()]
    if terms and not any(x in title for x in terms): return False
    locations=[x.lower() for x in cfg.get("location_keywords",[]) if x.strip()]
    if locations and not any(x in (job["location"] or "").lower() for x in locations): return False
    return True

def fingerprint(job):
    return hashlib.sha256((job["source"]+"|"+job["url"]).encode()).hexdigest()

def run_once():
    setup()
    cfg=config()
    started=datetime.now(timezone.utc).isoformat()
    found=inserted=0
    errors=[]
    tasks=[(greenhouse,b) for b in cfg.get("greenhouse_boards",[])]
    tasks += [(lever,s) for s in cfg.get("lever_sites",[])]
    def collect(task):
        fn,name=task
        return list(fn(name))
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(collect,t):t for t in tasks}
        for future in as_completed(futures):
            try:
                jobs=future.result()
                found+=len(jobs)
                with connect() as c:
                    for j in jobs:
                        if not match(j,cfg): continue
                        cur=c.execute("""INSERT OR IGNORE INTO discovery_jobs
                        (fingerprint,company,title,location,url,description,source,posted_at)
                        VALUES(?,?,?,?,?,?,?,?)""",(fingerprint(j),j["company"],j["title"],j["location"],
                            j["url"],j["description"],j["source"],str(j["posted_at"])))
                        inserted+=cur.rowcount
            except Exception as e:
                errors.append(str(futures[future][1])+": "+str(e))
    with connect() as c:
        c.execute("INSERT INTO discovery_runs(started_at,finished_at,found,inserted,errors) VALUES(?,?,?,?,?)",
            (started,datetime.now(timezone.utc).isoformat(),found,inserted,json.dumps(errors)))
    return {"found":found,"new":inserted,"errors":errors}

if __name__=="__main__":
    print(json.dumps(run_once(),indent=2))
