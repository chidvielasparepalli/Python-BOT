def get_unsolved_questions(page):
    try:
        # DOM-based direct scanner
        questions = page.evaluate("""() => {
            const list = [];
            const rows = document.querySelectorAll('[data-testid="question-list-question"]');
            rows.forEach(row => {
                const titleSpan = row.querySelector('span[title]');
                if (!titleSpan) return;
                const title = titleSpan.getAttribute('title').trim();
                
                const rowText = row.innerText.toUpperCase();
                if (!rowText.includes("SOLVED")) {
                    list.push(title);
                }
            });
            return list;
        }""")
        if questions:
            return questions
    except Exception as e:
        print(f"    [NAV] Error scanning DOM for questions: {e}")

    return []


def open_question(page, question_name):

    # Try exact title attribute match
    try:
        escaped_name = question_name.replace('"', '\\"')
        locator = page.locator(f'span[title="{escaped_name}"]').first
        locator.wait_for(timeout=3000)
        locator.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        locator.click(force=True)
        page.wait_for_selector(".monaco-editor, .ace_editor, textarea.inputarea, textarea", timeout=10000)
        page.wait_for_timeout(500)
        return True
    except Exception as e:
        print(f"    [NAV] Title attribute match failed for '{question_name}': {str(e)[:120]}")

    # Try exact text match
    try:
        locator = page.get_by_text(question_name, exact=True).first
        locator.wait_for(timeout=3000)
        locator.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        locator.click(force=True)
        page.wait_for_selector(".monaco-editor, .ace_editor, textarea.inputarea, textarea", timeout=10000)
        page.wait_for_timeout(500)
        return True
    except Exception as e:
        print(f"    [NAV] Exact text match failed for '{question_name}': {str(e)[:120]}")

    # Try partial / case-insensitive xpath match on title attribute
    try:
        clean_name = question_name.lower().strip()
        xpath = f"//span[contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{clean_name}')]"
        locator = page.locator(xpath).first
        locator.wait_for(timeout=3000)
        locator.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        locator.click(force=True)
        page.wait_for_selector(".monaco-editor, .ace_editor, textarea.inputarea, textarea", timeout=10000)
        page.wait_for_timeout(500)
        return True
    except Exception as e:
        print(f"    [NAV] XPath title match failed for '{question_name}': {str(e)[:120]}")

    # Try partial text match
    try:
        locator = page.get_by_text(question_name).first
        locator.wait_for(timeout=3000)
        locator.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        locator.click(force=True)
        page.wait_for_selector(".monaco-editor, .ace_editor, textarea.inputarea, textarea", timeout=10000)
        page.wait_for_timeout(500)
        return True
    except Exception as e:
        print(f"    [NAV] Partial text match failed for '{question_name}': {str(e)[:120]}")

    return False


def go_to_next_page(page):

    try:
        # Click the ">" (next) button
        next_btn = page.locator("button:has-text('\u203a'), button:has-text('>'), [class*='next'], [aria-label*='next'], [aria-label*='Next']").first

        if next_btn.is_visible(timeout=3000):
            next_btn.click()
            page.wait_for_timeout(3000)
            return True

    except:
        pass

    # Try clicking next page number
    try:
        # Get current page info
        pagination_text = page.locator("body").inner_text()
        
        # Find active page number and click next
        page_buttons = page.locator("button").all()
        found_active = False
        
        for btn in page_buttons:
            try:
                text = btn.inner_text().strip()
                classes = btn.get_attribute("class") or ""
                
                if found_active and text.isdigit():
                    btn.click()
                    page.wait_for_timeout(3000)
                    return True
                    
                if "active" in classes.lower() or "selected" in classes.lower():
                    found_active = True
            except:
                continue
    except:
        pass

    return False