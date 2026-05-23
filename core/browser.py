from playwright.sync_api import sync_playwright


def start_browser():

    playwright = sync_playwright().start()

    browser = playwright.chromium.launch_persistent_context(
        user_data_dir="./playwright_profile",
        headless=False,
        channel="chrome",
        args=[
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ]
    )

    # USE EXISTING TAB
    page = browser.pages[0]

    return playwright, browser, page