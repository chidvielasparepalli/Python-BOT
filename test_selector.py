from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    # LAUNCH STABLE BROWSER
    browser = p.chromium.launch_persistent_context(
        user_data_dir="./playwright_profile",
        headless=False,
        channel="chrome",
        args=[
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ]
    )

    page = browser.new_page()

    # OPEN PORTAL
    page.goto("https://learning.ccbp.in/")

    page.wait_for_load_state("networkidle")

    print("Portal opened")

    # OPEN QUESTION BANK
    page.get_by_text("Question Bank").first.click()

    page.wait_for_timeout(5000)

    print("Question bank opened")

    # APPLY FILTERS
    in_progress = page.get_by_text("In Progress").first

    in_progress.wait_for(timeout=10000)
    in_progress.click()

    print("Clicked In Progress")

    page.wait_for_timeout(3000)

    not_attempted = page.get_by_text("Not Attempted").first

    not_attempted.wait_for(timeout=10000)
    not_attempted.click()

    print("Clicked Not Attempted")

    page.wait_for_timeout(5000)

    print("\n=== FINDING UNSOLVED QUESTION ===\n")

    # TARGET FIRST UNSOLVED QUESTION
    question = page.get_by_text("Greatest Among N Numbers").first

    # WAIT FOR QUESTION
    question.wait_for(timeout=10000)

    # SCROLL INTO VIEW
    question.scroll_into_view_if_needed()

    page.wait_for_timeout(1000)

    # HIGHLIGHT FOR DEBUGGING
    question.highlight()

    page.wait_for_timeout(1000)

    print("Clicking question...")

    # STABLE CLICK
    question.click(force=True)

    print("Question opened!")

    # WAIT FOR QUESTION PAGE
    page.wait_for_load_state("domcontentloaded")

    page.wait_for_timeout(5000)

    print("Page stabilized")

    # EXTRACT PAGE TEXT
    problem_text = page.locator("body").inner_text()

    print("\n=== PROBLEM TEXT ===\n")

    print(problem_text[:5000])

    input("\nPress Enter to close...")

    browser.close()