def extract_problem(page):

    # ========================================
    # TRY TO GET JUST THE PROBLEM DESCRIPTION
    # ========================================

    try:

        # Try common problem description selectors
        selectors = [
            ".problem-description",
            ".question-content",
            ".problem-statement",
            ".coding-question",
            "[class*='problem']",
            "[class*='question']",
            "[class*='description']",
        ]

        for selector in selectors:

            try:

                el = page.locator(selector).first

                if el.is_visible(timeout=2000):

                    text = el.inner_text().strip()

                    if len(text) > 50:
                        return text[:12000]

            except:
                continue

    except:
        pass

    # ========================================
    # FALLBACK: GET FULL PAGE TEXT
    # ========================================

    text = page.locator("body").inner_text()

    return text[:12000]


def normalize_language(lang):
    if not lang:
        return "python"
    lang = lang.lower().strip()
    if "python" in lang or lang == "py":
        return "python"
    elif "javascript" in lang or lang == "js":
        return "javascript"
    elif "java" in lang:
        return "java"
    elif "cpp" in lang or "c++" in lang:
        return "c++"
    elif "c" in lang:
        return "c"
    elif "sql" in lang:
        return "sql"
    elif "html" in lang:
        return "html"
    elif "css" in lang:
        return "css"
    return lang


def detect_language(page):
    """
    Detects the programming language of the current question.
    Checks Monaco editor model language, active file tabs, or page text.
    """
    try:
        # 1. Check via Monaco Editor API
        lang = page.evaluate("""() => {
            if (typeof monaco !== 'undefined') {
                const editors = monaco.editor.getEditors();
                if (editors && editors.length > 0) {
                    return editors[0].getModel().getLanguageId();
                }
            }
            // Check select language dropdown
            const select = document.querySelector('select[class*="language"], select[id*="language"], [class*="select"] select');
            if (select) {
                return select.options[select.selectedIndex].value || select.options[select.selectedIndex].text;
            }
            return null;
        }""")
        if lang:
            detected = normalize_language(lang)
            print(f"    [LANG] Detected via Monaco/Select: {detected} (raw: {lang})")
            return detected
    except Exception as e:
        print(f"    [LANG] Monaco/Select detection failed: {e}")

    # 2. Check active tabs/filenames in the editor
    try:
        filename = page.evaluate("""() => {
            const activeTab = document.querySelector('.active-tab, .tab.active, [class*="tab"][class*="active"]');
            if (activeTab) return activeTab.innerText || activeTab.textContent;
            
            // Try any tab element
            const tabs = document.querySelectorAll('[class*="tab"]');
            for (const tab of tabs) {
                if (tab.className.includes('active') || tab.getAttribute('aria-selected') === 'true') {
                    return tab.innerText || tab.textContent;
                }
            }
            return null;
        }""")
        if filename:
            filename = filename.lower().strip()
            detected = None
            if filename.endswith(".py"):
                detected = "python"
            elif filename.endswith(".js"):
                detected = "javascript"
            elif filename.endswith(".java"):
                detected = "java"
            elif filename.endswith(".cpp") or filename.endswith(".c"):
                detected = "cpp"
            elif filename.endswith(".html"):
                detected = "html"
            elif filename.endswith(".css"):
                detected = "css"
            elif filename.endswith(".sql"):
                detected = "sql"
            
            if detected:
                normalized = normalize_language(detected)
                print(f"    [LANG] Detected via Tab: {normalized} (filename: {filename})")
                return normalized
    except Exception as e:
        print(f"    [LANG] Tab filename detection failed: {e}")

    # Default to python
    print("    [LANG] Could not detect language, defaulting to python")
    return "python"