@app.post("/linkedin/jobs")
def linkedin_jobs(req: JobRequest = Body(...)):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        jobs_collected = 0
        page_size = 25

        for start in range(0, req.limit, page_size):
            search_url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={req.job_title}&location={req.location}&start={start}"
            )
            page.goto(search_url)
            job_cards = page.query_selector_all("div.base-card")

            for card in job_cards:
                if jobs_collected >= req.limit:
                    break
                try:
                    role = card.query_selector("h3").inner_text().strip()
                    company = card.query_selector("h4").inner_text().strip()
                    link = card.query_selector("a.base-card__full-link").get_attribute("href")
                    if not link:
                        continue

                    # Easy Apply Mode
                    if req.mode.lower() == "easyapply":
                        badge = card.query_selector("span:has-text('Easy Apply')")
                        if not badge:
                            continue
                        results.append({
                            "role": role,
                            "company_name": company,
                            "linkedin_job_url": link
                        })

                    # Direct Apply Mode
                    elif req.mode.lower() == "directapply":
                        badge = card.query_selector("span:has-text('Easy Apply')")
                        if badge:
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
                        results.append({
                            "role": role,
                            "company_name": company,
                            "linkedin_job_url": link,
                            "company_apply_url": company_apply_url
                        })
                        job_page.close()

                    jobs_collected += 1

                except Exception:
                    continue

            if jobs_collected >= req.limit:
                break

        browser.close()

    return {
        "job_title": req.job_title,
        "location": req.location,
        "mode": req.mode,
        "results": results
    }
