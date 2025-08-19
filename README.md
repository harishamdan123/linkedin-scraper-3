# LinkedIn Scraper API (FastAPI + Playwright)

This is a simple LinkedIn job scraper that runs on Render with GitHub integration.  
It exposes a single endpoint you can call from **n8n**.

---

## 📦 API Endpoint

`POST /linkedin/jobs`

### Request Body
```json
{
  "job_title": "software engineer",
  "location": "India",
  "mode": "easyapply",   // "easyapply" or "directapply"
  "limit": 5
}
