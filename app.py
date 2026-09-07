import streamlit as st
import sqlite3, json, re
from urllib.parse import urlparse
from db import init, connect
from ai import generate
from discovery_page import render as render_discovery
from ranking_page import render as render_ranking
st.set_page_config(page_title="Auto Apply Job Finder",page_icon="💼",layout="wide")
init()
st.title("AUTO APPLY JOB FINDER")
st.caption("Local-first job discovery, truthful tailoring, human approval and application tracking.")
page=st.sidebar.radio("Workspace",["Dashboard","Master Profile","Jobs","Discovery","AI Ranking","Application Packages","Tracker"])
def rows(sql,args=()):
    with connect() as c: return [dict(r) for r in c.execute(sql,args).fetchall()]
def execute(sql,args=()):
    with connect() as c:
        cur=c.execute(sql,args)
        return cur.lastrowid
def profile():
    return "\n".join(f"{r['category']} | {r['label']}: {r['value']}" for r in rows("SELECT * FROM facts WHERE status='verified'"))
def valid_url(url):
    p=urlparse(url)
    return p.scheme in ("http","https") and bool(p.netloc)

if page=="Dashboard":
    a,b,c,d=st.columns(4)
    a.metric("Saved jobs",len(rows("SELECT id FROM jobs")))
    b.metric("Pending reviews",len(rows("SELECT id FROM packages WHERE status='pending'")))
    c.metric("Approved packages",len(rows("SELECT id FROM packages WHERE status='approved'")))
    d.metric("Applications",len(rows("SELECT id FROM applications WHERE status='applied'")))
    st.info("Save jobs → analyze → generate → review → approve → open application → submit yourself → track.")
    st.write("This MVP does not automatically scrape job boards, log into accounts, or submit applications.")
elif page=="Discovery":
    render_discovery()
elif page=="AI Ranking":
    render_ranking()

elif page=="Master Profile":
    st.header("Verified Candidate Profile")
    st.warning("Only verified facts are supplied to the AI. Review seeded facts before using them.")
    with st.form("fact"):
        category=st.text_input("Category")
        label=st.text_input("Fact label")
        value=st.text_area("Fact")
        status=st.selectbox("Verification",["needs_review","verified","do_not_use"])
        if st.form_submit_button("Add fact") and category and label and value:
            execute("INSERT INTO facts(category,label,value,status) VALUES(?,?,?,?)",(category,label,value,status))
            st.rerun()
    for r in rows("SELECT * FROM facts ORDER BY category,label"):
        with st.expander(f"{r['category']} · {r['label']} · {r['status']}"):
            with st.form(f"edit{r['id']}"):
                value=st.text_area("Value",r["value"])
                status=st.selectbox("Status",["verified","needs_review","do_not_use"],index=["verified","needs_review","do_not_use"].index(r["status"]))
                if st.form_submit_button("Save"):
                    execute("UPDATE facts SET value=?,status=? WHERE id=?",(value,status,r["id"]))
                    st.rerun()

elif page=="Jobs":
    st.header("Job Inbox")
    st.write("Paste a job description and its official application URL. Automated discovery is a later module.")
    with st.form("job"):
        company=st.text_input("Company")
        title=st.text_input("Role")
        location=st.text_input("Location")
        url=st.text_input("Official application URL")
        description=st.text_area("Job description",height=250)
        if st.form_submit_button("Save job"):
            if not company or not title or not description: st.error("Company, role and description are required.")
            elif url and not valid_url(url): st.error("Enter a valid HTTP(S) URL.")
            else:
                execute("INSERT INTO jobs(company,title,location,url,description) VALUES(?,?,?,?,?)",(company,title,location,url,description))
                st.success("Job saved.")
    for j in rows("SELECT * FROM jobs ORDER BY id DESC"):
        with st.expander(f"{j['company']} — {j['title']}"):
            st.caption(j["location"] or "")
            if j["url"]: st.link_button("Open job posting",j["url"])
            st.write(j["description"])
            if st.button("Analyze match",key=f"an{j['id']}"):
                try:
                    result=generate("VERIFIED PROFILE:\n"+profile()+"\nJOB:\n"+j["description"]+"\nProvide a justified 0-100 match score, strengths, missing requirements and recommendation. Do not invent qualifications.")
                    execute("UPDATE jobs SET analysis=? WHERE id=?",(result,j["id"]))
                    st.rerun()
                except Exception as e: st.error(f"Local AI unavailable: {e}")
            if j["analysis"]: st.markdown(j["analysis"])

elif page=="Application Packages":
    st.header("Application Packages")
    jobs=rows("SELECT * FROM jobs ORDER BY id DESC")
    if not jobs: st.info("Save a job first.")
    else:
        options={f"{j['company']} — {j['title']} (#{j['id']})":j for j in jobs}
        job=options[st.selectbox("Select job",list(options))]
        if st.button("Generate draft package"):
            try:
                content=generate("VERIFIED PROFILE:\n"+profile()+"\nTARGET COMPANY: "+job["company"]+"\nROLE: "+job["title"]+"\nJOB DESCRIPTION:\n"+job["description"]+"\nCreate: 1. Tailored resume content, 2. Cover letter, 3. Likely application answers, 4. Fact-check notes. Use only verified facts. Do not invent company facts. Flag missing information.")
                execute("INSERT INTO packages(job_id,content) VALUES(?,?)",(job["id"],content))
                st.rerun()
            except Exception as e: st.error(f"Local AI unavailable: {e}")
    for p in rows("SELECT p.*,j.company,j.title,j.url FROM packages p JOIN jobs j ON j.id=p.job_id ORDER BY p.id DESC"):
        with st.expander(f"{p['company']} — {p['title']} · {p['status']}"):
            with st.form(f"package{p['id']}"):
                content=st.text_area("Review and edit the complete package",p["content"],height=450)
                save=st.form_submit_button("Save edits")
                approve=st.form_submit_button("Approve this exact package",disabled=p["status"]=="approved")
                if save or approve:
                    execute("UPDATE packages SET content=?,status=? WHERE id=?",(content,"approved" if approve else "pending",p["id"]))
                    if approve:
                        execute("INSERT INTO applications(job_id,package_id) VALUES(?,?)",(p["job_id"],p["id"]))
                    st.rerun()
            if p["status"]=="approved":
                st.success("Approved. You remain responsible for reviewing and submitting the application.")
                if p["url"]: st.link_button("Open official application",p["url"])

elif page=="Tracker":
    st.header("Application Tracker")
    for a in rows("SELECT a.*,j.company,j.title,j.url FROM applications a JOIN jobs j ON j.id=a.job_id ORDER BY a.id DESC"):
        with st.expander(f"{a['company']} — {a['title']} · {a['status']}"):
            if a["url"]: st.link_button("Open application",a["url"])
            with st.form(f"track{a['id']}"):
                statuses=["approved_for_handoff","applied","screening","interview","offer","rejected","withdrawn"]
                status=st.selectbox("Status",statuses,index=statuses.index(a["status"]) if a["status"] in statuses else 0)
                notes=st.text_area("Notes",a["notes"] or "")
                if st.form_submit_button("Save status"):
                    execute("UPDATE applications SET status=?,notes=? WHERE id=?",(status,notes,a["id"]))
                    st.rerun()
