# Daily Work Tracker - Streamlit

A Streamlit version of the Daily Work Tracker.

## Features

- Dark mode
- Today's dashboard
- Add work
- Edit work
- Delete work
- Dynamic projects from the Google Sheet
- Work history by date
- Previous/Next day navigation
- Daily status summary
- Total time calculation

## Current backend

This version uses the existing Google Apps Script web app as the API, so no Google Sheet changes are required.

## Run locally on Windows

Open PowerShell in this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints, normally:

http://localhost:8501

## Important

The current Apps Script endpoint is publicly accessible. This is convenient for the first version, but for a production/private deployment we should later move the Streamlit app to authenticated Google Sheets API access using Streamlit secrets.
