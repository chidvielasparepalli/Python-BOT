def set_checkbox_state(page, value, target_checked):
    """
    Sets the checkbox with the given value to the target_checked state (True/False).
    Only clicks if the current state doesn't match the target state.
    """
    try:
        # Find the input element
        selector = f'input[value="{value}"]'
        input_el = page.locator(selector).first
        if input_el.count() > 0:
            is_checked = input_el.is_checked()
            if is_checked != target_checked:
                # We need to toggle it.
                # Since the input itself might be hidden/styled, let's click its parent label
                label_selector = f'label[data-testid="{value}-filter-option"]'
                label = page.locator(label_selector).first
                if label.count() > 0:
                    label.click()
                    print(f"    [FILTER] Toggled {value} to {target_checked}")
                else:
                    # Fallback to clicking input itself
                    input_el.click(force=True)
                    print(f"    [FILTER] Force-clicked input {value} to {target_checked}")
                return True
    except Exception as e:
        print(f"    [FILTER] Error setting checkbox {value} to {target_checked}: {e}")
    return False


def apply_unsolved_filters(page):
    """Apply In Progress + Not Attempted filters. Fast state-aware version."""

    # DISMISS ANY MODAL
    try:
        page.keyboard.press("Escape")
    except:
        pass

    try:
        # Wait up to 3s for filter checkboxes to load
        page.wait_for_selector('input[value="SOLVED"]', timeout=3000)
    except:
        pass

    changed = False

    # 1. SOLVED should be unchecked (False)
    if set_checkbox_state(page, "SOLVED", False):
        changed = True

    # 2. ATTEMPTED (In Progress) should be checked (True)
    if set_checkbox_state(page, "ATTEMPTED", True):
        changed = True

    # 3. NOT_ATTEMPTED (Not Attempted) should be checked (True)
    if set_checkbox_state(page, "NOT_ATTEMPTED", True):
        changed = True

    if changed:
        print("    [FILTER] Filter states updated, waiting for question list to refresh...")
        page.wait_for_timeout(1000)
    else:
        print("    [FILTER] Filters already correct, skipping clicks")


def reapply_filters(page):
    """Re-apply filters after returning to question list. Fast state-aware check."""
    apply_unsolved_filters(page)
    
    # Wait for the table/list rows to render and stabilize
    try:
        page.wait_for_selector('[data-testid="question-list-question"]', timeout=5000)
        page.wait_for_timeout(1000)
    except:
        pass