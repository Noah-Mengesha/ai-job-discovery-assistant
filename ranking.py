import json, re, sqlite3, os
from pathlib import Path
from datetime import datetime, timezone
from ai import generate

BASE=Path(__file__).resolve().parent
DB=BASE/"job_finder.db"
def conn():
    c=sqlite3.connect(DB, timeout=30)
    c.row_factory=sqlite3.Row
    return c
def init():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS job_rankings (
        job_id INTEGER PRIMARY KEY, score INTEGER, category TEXT,
        eligibility TEXT, sponsorship TEXT, location_fit TEXT,
        experience_fit TEXT, evidence TEXT, missing TEXT, recommendation TEXT,
        reviewed_at TEXT)""")
def profile():
    with conn() as c:
        return "\n".join(f"{r['category']} | {r['label']}: {r['value']}" for r in c.execute(
            "SELECT category,label,value FROM facts WHERE status='verified'"))
def extract_json(text):
    text=re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try: return json.loads(text)
    except json.JSONDecodeError:
        m=re.search(r"\{.*\}",text,re.S)
        if not m: raise ValueError("AI did not return a JSON object")
        return json.loads(m.group())
def rank_job(job, facts):
    prompt="""You are a conservative job eligibility and resume-fit reviewer.
Use ONLY the verified profile and the supplied job posting. Never invent facts.
The candidate seeks US remote roles or hybrid/on-site roles in the Minneapolis/Twin Cities area, internships and entry-level full-time positions, and needs future employer sponsorship. Expected graduation: December 2026.
Do not assume current work authorization, CPT/OPT eligibility, STEM OPT eligibility, or sponsorship from company reputation.
A posting's explicit restrictions must be respected. Unknown information is not a rejection.
Return ONLY a valid JSON object with these keys:
score (integer 0-100), category (strong_match/possible_match/low_match),
eligibility (promising/needs_verification/explicit_conflict),
sponsorship (explicitly_available/needs_verification/explicitly_unavailable),
location_fit (match/needs_verification/conflict),
experience_fit (match/stretch/conflict),
evidence (array of short factual strengths), missing (array of missing requirements),
recommendation (short explanation).
Score reflects technical fit, experience level, and location; do not award sponsorship certainty for unknowns.
An explicit work authorization or sponsorship conflict must be flagged, not hidden by a high score.
VERIFIED PROFILE:
"""+facts+"\nJOB:\n"+json.dumps(job,ensure_ascii=False)
    data=extract_json(generate(prompt))
    score=max(0,min(100,int(data["score"])))
    def choice(key,allowed):
        v=str(data.get(key,""))
        return v if v in allowed else allowed[0]
    return dict(score=score,
        category=choice("category",["low_match","possible_match","strong_match"]),
        eligibility=choice("eligibility",["needs_verification","promising","explicit_conflict"]),
        sponsorship=choice("sponsorship",["needs_verification","explicitly_available","explicitly_unavailable"]),
        location_fit=choice("location_fit",["needs_verification","match","conflict"]),
        experience_fit=choice("experience_fit",["stretch","match","conflict"]),
        evidence=json.dumps(data.get("evidence",[])),missing=json.dumps(data.get("missing",[])),
        recommendation=str(data.get("recommendation","")))
def save(job_id, result):
    with conn() as c:
        c.execute("""INSERT OR REPLACE INTO job_rankings
        (job_id,score,category,eligibility,sponsorship,location_fit,experience_fit,evidence,missing,recommendation,reviewed_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",(job_id,*[result[k] for k in
        ["score","category","eligibility","sponsorship","location_fit","experience_fit","evidence","missing","recommendation"]],
        datetime.now(timezone.utc).isoformat()))
def rank_pending(limit=10,refresh=False):
    init()
    facts=profile()
    if not facts: raise ValueError("Verify your Master Profile before ranking.")
    with conn() as c:
        sql="""SELECT d.* FROM discovery_jobs d LEFT JOIN job_rankings r ON r.job_id=d.id
        WHERE d.status!='dismissed' AND (r.job_id IS NULL OR ?) ORDER BY d.id DESC LIMIT ?"""
        jobs=[dict(r) for r in c.execute(sql,(int(refresh),limit))]
    results=[]
    for job in jobs:
        try:
            result=rank_job(job,facts)
            save(job["id"],result)
            results.append({"job_id":job["id"],"score":result["score"],"error":None})
        except Exception as e:
            results.append({"job_id":job["id"],"error":str(e)})
    return results
