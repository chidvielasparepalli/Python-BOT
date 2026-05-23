def submit_code(page):

    # ========================================
    # FIND AND CLICK SUBMIT BUTTON
    # ========================================

    submit_selectors = [
        "button:has-text('Submit')",
        "button:has-text('SUBMIT')",
        "button:has-text('Submit Code')",
        "text=Submit >> button",
        "[data-testid*='submit']",
        ".submit-btn",
        ".submit-button",
    ]

    for selector in submit_selectors:

        try:

            btn = page.locator(selector).first

            if btn.is_visible(timeout=3000):

                btn.click()

                print("    [SUBMIT] Clicked submit button")

                page.wait_for_timeout(8000)

                return True

        except:
            continue

    print("    [SUBMIT] Could not find submit button")
    return False


def check_results(page):

    try:

        page.wait_for_timeout(3000)

        text = page.locator("body").inner_text().upper()

        if "ALL TEST CASES PASSED" in text or "SUCCESSFULLY" in text:
            return "passed"

        elif "PASSED" in text and "FAILED" not in text:
            return "passed"

        elif "FAIL" in text or "ERROR" in text or "WRONG" in text:
            return "failed"

        else:
            return "unknown"

    except:
        return "unknown"
