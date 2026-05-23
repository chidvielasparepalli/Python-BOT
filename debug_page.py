from core.browser import start_browser

playwright, browser, page = start_browser()

try:
    page.goto("https://learning.ccbp.in/problems-set", timeout=120000, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    # Screenshot
    page.screenshot(path="debug_screenshot.png", full_page=True)
    print("Screenshot saved to debug_screenshot.png")

    # Dump visible text
    text = page.locator("body").inner_text()
    with open("debug_page_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Page text saved to debug_page_text.txt")

    # Print first 3000 chars
    print("\n=== PAGE TEXT (first 3000 chars) ===\n")
    print(text[:3000])

except Exception as e:
    print(f"Error: {e}")
    page.screenshot(path="debug_error_screenshot.png")
    print("Error screenshot saved")

finally:
    input("Press Enter to close browser...")
    browser.close()
    playwright.stop()
