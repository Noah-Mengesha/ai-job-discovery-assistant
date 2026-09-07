# Automatic discovery upgrade

This is an add-on for the existing local Streamlit application. It does not replace your database or resume files.

## Install
1. Stop Streamlit with Ctrl+C.
2. Back up your existing project folder.
3. Copy discovery.py, scheduler.py, discovery_page.py and search_config.json into the folder containing app.py.
4. Edit app.py: add `from discovery_page import render as render_discovery` near the imports.
5. Add "Discovery" to the sidebar radio options.
6. Add `elif page=="Discovery": render_discovery()` to the page routing chain.
7. Start Streamlit again.

## Configure sources
In Discovery, enter actual Greenhouse board tokens or Lever site tokens for companies you want to search. A board token is the identifier in the company's public job-board URL. Do not guess tokens; verify the public board first. The initial source lists are empty intentionally.

Examples of URL patterns:
https://job-boards.greenhouse.io/BOARDTOKEN
https://jobs.lever.co/SITETOKEN

The program uses the public JSON endpoints for these systems. Some companies use other ATS providers and are not covered. A failed or blocked source is reported, not bypassed.

## Test
From the project folder, using the virtual environment in the parent folder:
..\.venv\Scripts\python.exe discovery.py

## Background search
Run this in a separate PowerShell window:
..\.venv\Scripts\python.exe scheduler.py

It searches immediately, then repeats at the configured interval. Keep that window open. Closing the dashboard does not stop this separate scheduler.

## Windows Task Scheduler
Use Task Scheduler > Create Task.
Trigger: At log on.
Action: Start a program.
Program: C:\Users\noahi\Desktop\Auto Apply job finder\.venv\Scripts\python.exe
Arguments: scheduler.py
Start in: C:\Users\noahi\Desktop\Auto Apply job finder\auto_apply_job_finder
Select "Run only when user is logged on" for initial testing. Do not configure a second scheduler while the first is running.

## Limitations
No guaranteed coverage, no automatic application submission, no cloud hosting, no background execution while the computer is powered off. Discovery uses public board endpoints and does not scrape LinkedIn/Indeed or bypass anti-bot controls. Local SQLite is suitable for one local worker and dashboard, not a shared cloud deployment. AI ranking remains in the existing application inbox.
