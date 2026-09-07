import streamlit as st
import json
from ranking import init, conn, rank_pending, rank_job, profile, save

def render():
    init()
    st.header("AI Job Ranking")
    st.caption("Local AI screening using verified resume facts. Scores are estimates, not hiring probabilities.")
    st.warning("Sponsorship and work authorization are not verified automatically. Review the official posting and confirm uncertain eligibility with the employer or your international student office.")
    with conn() as c:
        total=c.execute("SELECT COUNT(*) FROM discovery_jobs").fetchone()[0]
        ranked=c.execute("SELECT COUNT(*) FROM job_rankings").fetchone()[0]
    st.write(f"Discovered: {total} · Ranked: {ranked}")
    limit=st.number_input("Jobs to rank in this batch",1,50,5)
    refresh=st.checkbox("Re-rank previously reviewed jobs",value=False)
    if st.button("Rank jobs with local AI"):
        with st.spinner("Reviewing job descriptions..."):
            try:
                results=rank_pending(int(limit),refresh)
                st.success(f"Reviewed {sum(not r.get('error') for r in results)} jobs.")
                for r in results:
                    if r.get("error"): st.error(f"Job {r['job_id']}: {r['error']}")
            except Exception as e: st.error(str(e))
    with conn() as c:
        data=[dict(r) for r in c.execute("""SELECT d.*,r.score,r.category,r.eligibility,r.sponsorship,
        r.location_fit,r.experience_fit,r.evidence,r.missing,r.recommendation
        FROM discovery_jobs d JOIN job_rankings r ON r.job_id=d.id
        ORDER BY CASE WHEN r.eligibility='explicit_conflict' OR r.sponsorship='explicitly_unavailable'
        OR r.location_fit='conflict' THEN 1 ELSE 0 END, r.score DESC""")]
    show_conflicts=st.checkbox("Show jobs with explicit eligibility/location conflicts",False)
    for j in data:
        conflict=j["eligibility"]=="explicit_conflict" or j["sponsorship"]=="explicitly_unavailable" or j["location_fit"]=="conflict"
        if conflict and not show_conflicts: continue
        with st.expander(f"{j['score']}/100 · {j['company']} — {j['title']}"):
            st.write(j["recommendation"])
            st.write("**Eligibility:**",j["eligibility"]," | **Sponsorship:**",j["sponsorship"])
            st.write("**Location:**",j["location_fit"]," | **Experience:**",j["experience_fit"])
            st.write("**Strengths:**")
            for item in json.loads(j["evidence"]):
                st.write("• " + str(item))
            st.write("**Missing / verify:**")
            for item in json.loads(j["missing"]):
                st.write("• " + str(item))
            if j["url"]: st.link_button("Official posting",j["url"])
            if st.button("Re-rank this job",key=f"rerank{j['id']}"):
                try:
                    with st.spinner("Reviewing..."):
                        save(j["id"],rank_job(j,profile()))
                    st.rerun()
                except Exception as e: st.error(str(e))
            if st.button("Add to application inbox",key=f"add_rank{j['id']}"):
                with conn() as c:
                    existing=c.execute("SELECT id FROM jobs WHERE url=?",(j["url"],)).fetchone()
                    if existing: st.info("Already in application inbox.")
                    else:
                        c.execute("INSERT INTO jobs(company,title,location,url,description) VALUES(?,?,?,?,?)",
                        (j["company"],j["title"],j["location"],j["url"],j["description"]))
                        st.success("Added to application inbox.")
