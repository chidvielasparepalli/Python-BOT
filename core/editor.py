import time


def inject_code(page, code):
    """
    Injects code into the editor, bypassing paste protection.
    Supports Monaco Editor and Ace Editor.
    Uses multiple methods in order of reliability.
    """

    # ========================================
    # METHOD 1: EDITOR setValue() API (FASTEST)
    # Directly sets content via Monaco/Ace's JS API
    # This completely bypasses paste protection
    # ========================================

    try:

        result = page.evaluate("""(code) => {
            // Try Ace Editor first (from DOM)
            try {
                const aceEditorEl = document.querySelector('.ace_editor');
                if (aceEditorEl && aceEditorEl.env && aceEditorEl.env.editor) {
                    aceEditorEl.env.editor.setValue(code, -1);
                    return 'ace_dom';
                }
            } catch(e) {}

            // Try Ace Editor global
            try {
                if (typeof ace !== 'undefined') {
                    const editorEl = document.querySelector('.ace_editor');
                    if (editorEl) {
                        const editor = ace.edit(editorEl);
                        if (editor) {
                            editor.setValue(code, -1);
                            return 'ace_global';
                        }
                    }
                }
            } catch(e) {}

            // Try global monaco object
            if (typeof monaco !== 'undefined') {
                try {
                    const editors = monaco.editor.getEditors();
                    if (editors && editors.length > 0) {
                        editors[0].setValue(code);
                        return 'monaco_global';
                    }
                } catch(e) {}
            }

            // Try finding monaco through DOM element
            try {
                const editorEl = document.querySelector('.monaco-editor');
                if (editorEl) {
                    const keys = Object.keys(editorEl);
                    for (const key of keys) {
                        if (key.startsWith('__') || key.startsWith('_')) {
                            const val = editorEl[key];
                            if (val && typeof val === 'object' && val.setValue) {
                                val.setValue(code);
                                return 'monaco_dom';
                            }
                        }
                    }
                }
            } catch(e) {}

            // Try through model
            try {
                if (typeof monaco !== 'undefined') {
                    const models = monaco.editor.getModels();
                    if (models && models.length > 0) {
                        models[0].setValue(code);
                        return 'monaco_model';
                    }
                }
            } catch(e) {}

            return false;
        }""", code)

        if result:
            print(f"    [EDITOR] Injected via {result}")
            page.wait_for_timeout(1000)
            return True

    except Exception as e:
        print(f"    [EDITOR] API setValue failed: {e}")


    # ========================================
    # METHOD 2: CDP Input.insertText
    # Uses Chrome DevTools Protocol directly
    # Bypasses ALL JavaScript event handlers
    # ========================================

    try:
        # Focus the editor (force click to avoid interception errors)
        editor_sel = ".monaco-editor textarea, .ace_editor textarea, textarea.inputarea, textarea, .ace_text-input"
        editor = page.locator(editor_sel).first

        if editor.is_visible(timeout=5000):

            editor.click(force=True)
            page.wait_for_timeout(300)

            # Select all existing content
            page.keyboard.press("Control+A")
            page.wait_for_timeout(200)
            page.keyboard.press("Delete")
            page.wait_for_timeout(300)

            # Use CDP to insert text - this is the nuclear option
            # It bypasses all JS paste handlers
            cdp = page.context.new_cdp_session(page)
            cdp.send("Input.insertText", {"text": code})
            cdp.detach()

            print("    [EDITOR] Injected via CDP Input.insertText")
            page.wait_for_timeout(1000)
            return True

    except Exception as e:
        print(f"    [EDITOR] CDP insertText failed: {e}")


    # ========================================
    # METHOD 3: Playwright keyboard.insert_text
    # Similar to CDP but through Playwright API
    # ========================================

    try:
        editor_sel = ".monaco-editor, .ace_editor, textarea"
        editor = page.locator(editor_sel).first

        if editor.is_visible(timeout=3000):

            editor.click(force=True)
            page.wait_for_timeout(300)

            page.keyboard.press("Control+A")
            page.wait_for_timeout(200)
            page.keyboard.press("Delete")
            page.wait_for_timeout(300)

            # Playwright's insert_text uses CDP internally
            page.keyboard.insert_text(code)

            print("    [EDITOR] Injected via keyboard.insert_text")
            page.wait_for_timeout(1000)
            return True

    except Exception as e:
        print(f"    [EDITOR] insert_text failed: {e}")


    # ========================================
    # METHOD 4: JavaScript execCommand
    # Forces text insertion via document API
    # ========================================

    try:
        editor_sel = ".monaco-editor textarea, .ace_editor textarea, textarea.inputarea, textarea, .ace_text-input"
        editor = page.locator(editor_sel).first

        if editor.is_visible(timeout=3000):

            editor.click(force=True)
            page.wait_for_timeout(300)

            page.keyboard.press("Control+A")
            page.wait_for_timeout(200)

            page.evaluate("""(code) => {
                const ta = document.querySelector('.monaco-editor textarea, .ace_editor textarea, textarea.inputarea, textarea, .ace_text-input');
                if (ta) {
                    ta.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('insertText', false, code);
                }
            }""", code)

            print("    [EDITOR] Injected via execCommand")
            page.wait_for_timeout(1000)
            return True

    except Exception as e:
        print(f"    [EDITOR] execCommand failed: {e}")


    # ========================================
    # METHOD 5: Override paste event + Ctrl+V
    # Removes paste listeners then pastes
    # ========================================

    try:
        editor = page.locator(".monaco-editor, .ace_editor, textarea").first

        if editor.is_visible(timeout=3000):

            # Remove all paste event listeners and override clipboard
            page.evaluate("""(code) => {
                // Store code in window for paste handler
                window.__injected_code = code;

                // Override clipboard read
                const origRead = navigator.clipboard.readText;
                navigator.clipboard.readText = () => Promise.resolve(code);
                navigator.clipboard.writeText(code);

                // Remove paste prevention handlers
                const editors = document.querySelectorAll('.monaco-editor, .ace_editor, textarea, [contenteditable]');
                editors.forEach(el => {
                    const clone = el.cloneNode(true);
                    el.parentNode.replaceChild(clone, el);
                });

                // Add our own paste handler
                document.addEventListener('paste', function(e) {
                    e.stopImmediatePropagation();
                    const text = window.__injected_code || code;
                    if (e.target.value !== undefined) {
                        e.target.value = text;
                    }
                    document.execCommand('insertText', false, text);
                }, true);
            }""", code)

            page.wait_for_timeout(500)

            editor = page.locator(".monaco-editor, .ace_editor, textarea").first
            editor.click(force=True)
            page.keyboard.press("Control+A")
            page.wait_for_timeout(200)
            page.keyboard.press("Control+V")

            print("    [EDITOR] Injected via clipboard override + Ctrl+V")
            page.wait_for_timeout(1000)
            return True

    except Exception as e:
        print(f"    [EDITOR] Clipboard override failed: {e}")


    # ========================================
    # METHOD 6: TYPING (LAST RESORT - SLOW)
    # Types each character individually
    # ========================================

    try:
        editor = page.locator(".monaco-editor, .ace_editor, textarea").first

        if editor.is_visible(timeout=3000):

            editor.click(force=True)
            page.wait_for_timeout(300)

            page.keyboard.press("Control+A")
            page.keyboard.press("Delete")
            page.wait_for_timeout(300)

            # Type line by line with minimal delay
            for line in code.split("\n"):
                page.keyboard.type(line, delay=3)
                page.keyboard.press("Enter")

            print("    [EDITOR] Injected via typing (slow)")
            page.wait_for_timeout(1000)
            return True

    except Exception as e:
        print(f"    [EDITOR] Typing failed: {e}")


    print("    [EDITOR] ALL INJECTION METHODS FAILED!")
    return False