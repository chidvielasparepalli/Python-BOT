from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir="user_data",
        headless=False
    )

    page = context.new_page()

    page.goto("https://learning.ccbp.in/problems-set.com")

    print("Logged in automatically.")

    input("Press Enter to close.")

    context.close()