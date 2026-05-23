import time
import traceback

from core.browser import start_browser
from core.filters import apply_unsolved_filters, reapply_filters
from core.navigator import get_unsolved_questions, open_question, go_to_next_page
from core.extractor import extract_problem, detect_language
from core.solver import solve_problem
from core.editor import inject_code
from core.submitter import submit_code, check_results
from core.progress import load_progress, save_progress, mark_completed, mark_failed, is_completed


# ============================================================
# FAST PRINT LOGGER (NO TTS)
# ============================================================

def log(msg):
    print(f"[BOT] {msg}")


def take_screenshot(page, name="debug_screenshot.png"):
    try:
        page.screenshot(path=name)
    except:
        pass


# ============================================================
# CONFIG
# ============================================================

LMS_URL = "https://learning.ccbp.in/problems-set"
MAX_RETRIES = 2
MAX_CONSECUTIVE_ERRORS = 10


# ============================================================
# START
# ============================================================

log("=== NIAT ASSIGNMENT BOT - TURBO MODE ===")

progress = load_progress()
log(f"Completed: {len(progress['completed'])} | Failed: {len(progress['failed'])}")

# Reset failed list so we retry them
progress["failed"] = []
save_progress(progress)

playwright, browser, page = start_browser()

total_solved = 0
total_skipped = 0
total_failed = 0
consecutive_errors = 0
start_time = time.time()


def check_and_recover_browser():
    global playwright, browser, page
    try:
        page.evaluate("1")
        return True
    except Exception as e:
        log("Browser crashed or closed. Recovering...")
        try:
            browser.close()
        except:
            pass
        try:
            playwright.stop()
        except:
            pass
        
        try:
            playwright, browser, page = start_browser()
            log("Browser restarted. Re-opening LMS...")
            page.goto(LMS_URL, timeout=120000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            reapply_filters(page)
            return False
        except Exception as re_err:
            log(f"Failed to restart browser: {re_err}")
            return False


try:

    # ============================================================
    # OPEN LMS
    # ============================================================

    log("Opening LMS...")
    page.goto(LMS_URL, timeout=120000, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    take_screenshot(page, "debug_lms.png")

    # Dismiss modal
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
    except:
        pass

    # ============================================================
    # APPLY FILTERS
    # ============================================================

    log("Applying filters...")
    apply_unsolved_filters(page)
    page.wait_for_timeout(2000)
    take_screenshot(page, "debug_filtered.png")


    # ============================================================
    # MAIN LOOP - DYNAMIC SINGLE-QUESTION LOOP
    # ============================================================

    page_number = 1
    run_failed_questions = set()

    while True:

        log(f"\n{'='*50}")
        log(f"PAGE {page_number}")
        log(f"{'='*50}")

        # Ensure browser is healthy before scanning
        check_and_recover_browser()

        # GET QUESTIONS
        questions = get_unsolved_questions(page)
        log(f"Found {len(questions)} unsolved questions in DOM")

        # Find the first target question that has not been completed/failed
        target_q = None
        for qname in questions:
            if not is_completed(progress, qname) and qname not in run_failed_questions:
                target_q = qname
                break

        # If no target questions left on this page, move to next page
        if not target_q:
            log("No unsolved questions on this page, loading next page...")
            if go_to_next_page(page):
                page_number += 1
                page.wait_for_timeout(2000)
                reapply_filters(page)
                continue
            else:
                log("No more pages available!")
                break

        qname = target_q
        elapsed = time.time() - start_time
        rate = total_solved / (elapsed / 60) if elapsed > 60 else 0
        log(f"\n[TARGET] {qname}")
        log(f"Stats: {total_solved} solved | {total_failed} failed | {rate:.1f}/min")

        success = False

        for attempt in range(1, MAX_RETRIES + 1):

            try:
                # Ensure browser is healthy
                check_and_recover_browser()

                # OPEN QUESTION
                if not open_question(page, qname):
                    log(f"  Cannot open, skipping")
                    break

                page.wait_for_timeout(500)
                take_screenshot(page, "debug_question.png")

                # EXTRACT
                problem = extract_problem(page)
                if not problem or len(problem) < 20:
                    log(f"  Empty problem, skipping")
                    try:
                        page.go_back()
                        page.wait_for_url("**/problems-set", timeout=5000)
                        page.wait_for_timeout(1000)
                    except:
                        page.wait_for_timeout(1500)
                    reapply_filters(page)
                    break

                # DETECT LANGUAGE
                language = detect_language(page)

                # SOLVE
                log(f"  Solving ({language})...")
                code = solve_problem(problem, language)
                if not code or len(code) < 5:
                    log(f"  Empty solution, retry")
                    try:
                        page.go_back()
                        page.wait_for_url("**/problems-set", timeout=5000)
                        page.wait_for_timeout(1000)
                    except:
                        page.wait_for_timeout(1500)
                    reapply_filters(page)
                    continue

                log(f"  Got {len(code)} chars of code")

                # INJECT (FORCE PASTE)
                log(f"  Injecting code...")
                if not inject_code(page, code):
                    log(f"  Injection failed, retry")
                    try:
                        page.go_back()
                        page.wait_for_url("**/problems-set", timeout=5000)
                        page.wait_for_timeout(1000)
                    except:
                        page.wait_for_timeout(1500)
                    reapply_filters(page)
                    continue

                page.wait_for_timeout(1000)
                take_screenshot(page, "debug_injected.png")

                # SUBMIT
                log(f"  Submitting...")
                submitted = submit_code(page)
                if submitted:
                    result = check_results(page)
                    log(f"  Result: {result}")
                take_screenshot(page, "debug_submitted.png")

                # MARK DONE
                mark_completed(progress, qname)
                total_solved += 1
                success = True
                consecutive_errors = 0

                # GO BACK
                try:
                    page.go_back()
                    page.wait_for_url("**/problems-set", timeout=5000)
                    page.wait_for_timeout(1000)
                except:
                    page.wait_for_timeout(1500)

                # RE-APPLY FILTERS (key fix!)
                reapply_filters(page)
                break

            except Exception as e:
                log(f"  ERROR attempt {attempt}: {str(e)[:150]}")
                consecutive_errors += 1
                take_screenshot(page, "debug_error.png")

                # Recover browser if crashed/closed
                check_and_recover_browser()

                try:
                    page.go_back()
                    page.wait_for_url("**/problems-set", timeout=5000)
                    page.wait_for_timeout(1000)
                    reapply_filters(page)
                except:
                    try:
                        page.wait_for_timeout(1500)
                        reapply_filters(page)
                    except:
                        pass

                if attempt < MAX_RETRIES:
                    time.sleep(2)

        if not success:
            mark_failed(progress, qname)
            run_failed_questions.add(qname)
            total_failed += 1

        if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
            log(f"Too many consecutive errors ({consecutive_errors}), stopping")
            break

        # Tiny delay between questions
        time.sleep(0.5)

    # ============================================================
    # DONE
    # ============================================================

    elapsed = time.time() - start_time
    log(f"\n{'='*50}")
    log(f"COMPLETED in {elapsed/60:.1f} minutes")
    log(f"Solved: {total_solved}")
    log(f"Skipped: {total_skipped}")
    log(f"Failed: {total_failed}")
    log(f"Total in progress: {len(progress['completed'])}")
    log(f"{'='*50}")

except Exception as e:
    log(f"CRASH: {str(e)[:300]}")
    traceback.print_exc()

finally:
    save_progress(progress)
    try:
        browser.close()
    except:
        pass
    try:
        playwright.stop()
    except:
        pass
    log("Bot shut down.")
