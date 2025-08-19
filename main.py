from fastapi import FastAPI, Body
from pydantic import BaseModel
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

app = FastAPI()

class JobRequest(BaseModel):
    job_title: str
    location: str = "India"
    mode: str = "easyapply"  # "easyapply" or "directapply"
    limit: int = 10


@app.post("/linkedin/jobs")
def linkedin_jobs(req: JobRequest = Body(...)):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # LinkedIn Jobs Search
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={req.job_title}&location={req.location}"
        page.goto(search_url)

        # Collect job cards
        job_cards = page.query_selector_all("div.base-card")[:req.limit]

        for card in job_cards:
            try:
                role = card.query_selector("h3").inner_text().strip()
                company = card.query_selector("h4").inner_text().strip()
                link = card.query_selector("a.base-card__full-link").get_attribute("href")

                if not link:
                    continue

                # -------------------
                # EASY APPLY MODE
                # -------------------
                if req.mode.lower() == "easyapply":
                    easy_apply_badge = card.query_selector("span:has-text('Easy Apply')")
                    if not easy_apply_badge:
                        continue
                    results.append({
                        "role": role,
                        "company_name": company,
                        "linkedin_job_url": link
                    })

                # -------------------
                # DIRECT APPLY MODE
                # -------------------
                elif req.mode.lower() == "directapply":
                    easy_apply_badge = card.query_selector("span:has-text('Easy Apply')")
                    if easy_apply_badge:
                        continue

                    job_page = context.new_page()
                    job_page.goto(link)

                    company_apply_url = None
                    try:
                        job_page.click("a[href*='applyRedirect']", timeout=5000)
                        job_page.wait_for_load_state("load")
                        popup = job_page.context.pages[-1]
                        company_apply_url = popup.url
                    except PWTimeout:
                        pass
                    except Exception:
                        pass

                    results.append({
                        "role": role,
                        "company_name": company,
                        "linkedin_job_url": link,
                        "company_apply_url": company_apply_url
                    })

                    job_page.close()

            except Exception:
                continue

        browser.close()

    return {
        "job_title": req.job_title,
        "location": req.location,
        "mode": req.mode,
        "results": results
    }
