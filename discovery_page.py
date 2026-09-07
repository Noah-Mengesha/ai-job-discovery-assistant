import streamlit as st
from discovery import setup, connect, run_once, config, CONFIG
import json
def render():
    setup()
    st.header("Automatic Job Discovery")
    st.caption("Searches configured public Greenhouse and Lever job boards. No login or application submission.")
    cfg=config()
    with st.form("discovery_config"):
        boards=st.text_area("Greenhouse board tokens (one per line)", "\n".join(cfg["greenhouse_boards"]))
        sites=st.text_area("Lever site tokens (one per line)", "\n".join(cfg["lever_sites"]))
        titles=st.text_area("Title keywords (one per line)", "\n".join(cfg["title_keywords"]))
        locations=st.text_area("Location keywords (blank = all locations)", "\n".join(cfg["location_keywords"]))
        hours=st.number_input("Check every N hours",1,24,int(cfg["interval_hours"]))
        senior=st.checkbox("Exclude senior/staff/principal roles",cfg["exclude_senior"])
        internships=st.checkbox("Exclude internships",cfg["exclude_internships"])
        if st.form_submit_button("Save search settings"):
            cfg.update(greenhouse_boards=boards.splitlines(),lever_sites=sites.splitlines(),
                title_keywords=titles.splitlines(),location_keywords=locations.splitlines(),
                interval_hours=int(hours),exclude_senior=senior,exclude_internships=internships)
            CONFIG.write_text(json.dumps(cfg,indent=2),encoding="utf-8")
            st.success("Saved.")
    if st.button("Search now"):
        with st.spinner("Checking configured boards..."):
            st.write(run_once())
    with connect() as c:
        jobs=[dict(r) for r in c.execute("SELECT * FROM discovery_jobs ORDER BY first_seen DESC LIMIT 300")]
        runs=[dict(r) for r in c.execute("SELECT * FROM discovery_runs ORDER BY id DESC LIMIT 5")]
    st.subheader("Recent searches")
    st.dataframe(runs,hide_index=True)
    st.subheader(f"Discovered jobs ({len(jobs)} shown)")
    for j in jobs:
        with st.expander(f"{j['company']} — {j['title']}"):
            st.write(j["location"])
            st.caption(j["source"]+" · "+str(j["posted_at"]))
            st.write(j["description"])
            if j["url"]: st.link_button("Open official posting",j["url"])
            if st.button("Add to application inbox",key="import"+str(j["id"])):
                from db import connect as main_connect
                with main_connect() as c:
                    existing=c.execute("SELECT id FROM jobs WHERE url=?",(j["url"],)).fetchone()
                    if existing: st.info("Already in inbox.")
                    else:
                        c.execute("INSERT INTO jobs(company,title,location,url,description) VALUES(?,?,?,?,?)",
                            (j["company"],j["title"],j["location"],j["url"],j["description"]))
                        st.success("Added to inbox.")
